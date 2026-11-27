"""Post-hoc diagnostic for H-rockera-01: the Paleozoic-share association inside chosen states.

Fits the pooled 2001-2023 county model with one Paleozoic slope per chosen state and one for every other
state (state fixed effects as usual), so each state's slope compares its own counties with each other.
Slopes are per national SD of Paleozoic share, so they compare directly with the national 1.106. Adds a
county table (observed vs expected from the controls-only model) for the chosen states. Descriptive only.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from uap_analytics.common.geo import COUNTY_ID

STATE_NAMES = {"04": "Arizona", "35": "New Mexico", "49": "Utah", "08": "Colorado", "32": "Nevada"}
PALEOZOIC = "share_paleozoic"


def slope_columns(table: pd.DataFrame, share: str, states: list[str]) -> tuple[pd.DataFrame, list[str]]:
    """Share in national SD units, split into one column per chosen state and one for the rest (0 elsewhere)."""
    z = (table[share] - table[share].mean()) / table[share].std(ddof=0)
    out, cols = table.copy(), []
    chosen = table["state_fips"].astype(str).isin(states)
    for s in states:
        col = f"slope_{s}"
        out[col] = np.where(table["state_fips"].astype(str) == s, z, 0.0)
        cols.append(col)
    out["slope_rest"] = np.where(~chosen, z, 0.0)
    cols.append("slope_rest")
    return out, cols


def per_national_sd(coef: pd.Series, column: pd.Series) -> dict:
    """The model z-scores each column; convert its rate ratio back to per national SD of the share."""
    sd = float(column.std(ddof=0))
    return {"rate_ratio": float(np.exp(np.log(coef["rate_ratio"]) / sd)),
            "ci_low": float(np.exp(np.log(coef["ci_low"]) / sd)),
            "ci_high": float(np.exp(np.log(coef["ci_high"]) / sd)), "p_value": float(coef["p_value"])}


class StateEraDiagnostics:
    def __init__(self, study) -> None:
        self.study = study
        self.states = list(getattr(study, "diag_states", None) or ["04", "35", "49"])

    def run(self) -> Path:
        st = self.study
        table, events, removed, _, _ = st.prepare()
        counts, _, nights = st._period_counts(events, removed, st._split_years(), table.index, st.PRIMARY)
        data, cols = slope_columns(table, PALEOZOIC, self.states)
        fit = st._fit(data, counts, nights, tuple(cols))
        used = data.loc[fit.fitted.index]
        slopes = {c: per_national_sd(fit.coefficients.loc[c], used[c]) for c in cols}
        national = st._fit(table, counts, nights, (PALEOZOIC,)).coefficients.loc[PALEOZOIC]

        base = st._fit(table, counts, nights)
        expected = base.fitted
        observed = counts.reindex(expected.index)
        names = st.counties.set_index(COUNTY_ID)
        name_col = next((c for c in ("NAME", "NAMELSAD", "name") if c in names.columns), None)

        f = lambda r: f"{r['rate_ratio']:.3f} ({r['ci_low']:.3f}–{r['ci_high']:.3f})"  # noqa: E731
        lines = ["# H-rockera-01 diagnostic: Paleozoic share by state (post hoc)", "",
                 f"Pooled {st._split_years()[0]}–2023, filtered tier, H-persist-01 controls, state fixed effects. "
                 "One Paleozoic slope per chosen state and one for all other states, each per national SD of "
                 "Paleozoic share (comparable with the national estimate). Descriptive only.", "",
                 f"National (one slope): {f(national)}, p {national['p_value']:.3g}.", "",
                 "Standard errors are clustered by state, so a slope that lives inside one state has a single "
                 "cluster and no valid confidence interval; per-state slopes are point estimates only.", "",
                 "| State | Counties | Mean Paleozoic share | Paleozoic slope (per national SD) |",
                 "| --- | --- | --- | --- |"]
        state = used["state_fips"].astype(str)
        for s in self.states:
            m = state == s
            lines.append(f"| {STATE_NAMES.get(s, s)} | {int(m.sum())} | {table.loc[m.index[m], PALEOZOIC].mean():.1%} | "
                         f"{slopes[f'slope_{s}']['rate_ratio']:.3f} (no valid CI) |")
        rest = ~state.isin(self.states)
        lines.append(f"| All other states | {int(rest.sum())} | {table.loc[rest.index[rest], PALEOZOIC].mean():.1%} | "
                     f"{f(slopes['slope_rest'])}, p {slopes['slope_rest']['p_value']:.3g} |")

        for s in self.states:
            idx = state.index[state == s]
            sub = pd.DataFrame({"county": names.loc[idx, name_col] if name_col else idx,
                                "paleozoic": table.loc[idx, PALEOZOIC], "observed": observed.loc[idx],
                                "expected": expected.loc[idx]}).sort_values("paleozoic", ascending=False)
            sub["ratio"] = sub["observed"] / sub["expected"]
            rho, p = spearmanr(sub["paleozoic"], np.log((sub["observed"] + 0.5) / (sub["expected"] + 0.5)))
            hi = sub["paleozoic"] >= sub["paleozoic"].median()
            o_hi, e_hi = sub.loc[hi, "observed"].sum(), sub.loc[hi, "expected"].sum()
            o_lo, e_lo = sub.loc[~hi, "observed"].sum(), sub.loc[~hi, "expected"].sum()
            lines += ["", f"## {STATE_NAMES.get(s, s)}", "",
                      f"Spearman (Paleozoic share vs log observed/expected): {rho:.2f} (p {p:.2g}). Counties at or above "
                      f"the state's median share: observed/expected {o_hi / e_hi:.2f} ({int(o_hi):,} / {e_hi:,.0f}); "
                      f"below: {o_lo / e_lo:.2f} ({int(o_lo):,} / {e_lo:,.0f}).", "",
                      "| County | Paleozoic share | Observed | Expected | Ratio |", "| --- | --- | --- | --- | --- |"]
            for r in sub.itertuples():
                lines.append(f"| {r.county} | {r.paleozoic:.0%} | {int(r.observed):,} | {r.expected:,.1f} | {r.ratio:.2f} |")
        out = st.root / "results" / st.HYPOTHESIS_ID / "diagnostics"
        out.mkdir(parents=True, exist_ok=True)
        path = out / f"states_{'_'.join(self.states)}.md"
        path.write_text("\n".join(lines) + "\n")
        return path


class LandUseEraDiagnostics:
    """Post hoc: does the Paleozoic association survive land-use controls (NLCD 2011 shares) and a control for
    young sediment cover over bedrock (unconsolidated share, all eras)? Pooled 2001-2023, filtered tier."""

    def __init__(self, study) -> None:
        self.study = study

    def _land_cover(self, table: pd.DataFrame) -> pd.DataFrame:
        from uap_analytics.features.land_cover import county_land_cover

        st = self.study
        counties = st.counties[[COUNTY_ID, "geometry"]].reset_index(drop=True)
        return county_land_cover(st.sources.land_cover().load(), counties, counties[COUNTY_ID].to_numpy()).reindex(table.index)

    def run(self) -> Path:
        from uap_analytics.features.land_cover import GROUPS
        from uap_analytics.features.rock_age import ERA_NAMES
        from uap_analytics.common.geo import M_PER_KM
        from uap_analytics.hypotheses.rock_age import two_sided_shift_p

        st = self.study
        table, events, removed, summary, _ = st.prepare()
        lc = self._land_cover(table)
        table = table.join(lc)
        table["share_unconsolidated_all"] = table[[f"share_{e}_unconsolidated" for e in ERA_NAMES]].sum(axis=1)
        land = tuple(f"lc_{g}" for g in GROUPS)
        cover = ("share_unconsolidated_all",)
        counts, _, nights = st._period_counts(events, removed, st._split_years(), table.index, st.PRIMARY)

        f = lambda r: f"{r['rate_ratio']:.3f} ({r['ci_low']:.3f}–{r['ci_high']:.3f})"  # noqa: E731
        models = {"Paleozoic alone": (), "+ land cover": land, "+ sediment cover": cover,
                  "+ land cover + sediment cover": land + cover}
        fits = {name: st._fit(table, counts, nights, (PALEOZOIC, *extra)) for name, extra in models.items()}
        full = land + cover

        lines = ["# H-rockera-01 diagnostic: Paleozoic share with land-use controls (post hoc)", "",
                 "Pooled 2001–2023, filtered tier, H-persist-01 controls, state fixed effects, state-clustered SEs. "
                 "Land cover: NLCD 2011 shares per county (480 m cells): developed, forest, shrub/grass, pasture, "
                 "cropland, wetland (water and barren are the reference). Sediment cover: share of the county's "
                 "surface mapped as unconsolidated deposits, any era (SGMC). Descriptive only.", "",
                 "| Model | Paleozoic share (per SD) | p |", "| --- | --- | --- |"]
        for name, fit in fits.items():
            r = fit.coefficients.loc[PALEOZOIC]
            lines.append(f"| {name} | {f(r)} | {r['p_value']:.3g} |")

        coef = fits["+ land cover + sediment cover"].coefficients
        lines += ["", "## Control terms in the full model (per SD)", "", "| Term | Rate ratio | p |", "| --- | --- | --- |"]
        for t in full:
            lines.append(f"| {t} | {f(coef.loc[t])} | {coef.loc[t, 'p_value']:.3g} |")

        corr = table[[PALEOZOIC, *full]].corr().loc[PALEOZOIC, list(full)]
        lines += ["", "Correlation of Paleozoic share with the controls (all counties): " +
                  ", ".join(f"{k} {v:+.2f}" for k, v in corr.items()) + "."]

        from uap_analytics.hypotheses.rock_era import PERIODS
        lines += ["", "## Full model by period", "", "| Period | Paleozoic share (per SD) | p |", "| --- | --- | --- |"]
        for label, yrs in PERIODS.items():
            c, _, n = st._period_counts(events, removed, yrs, table.index, st.PRIMARY)
            r = st._fit(table, c, n, (PALEOZOIC, *full)).coefficients.loc[PALEOZOIC]
            lines.append(f"| {label} | {f(r)} | {r['p_value']:.3g} |")

        # Leave one state out.
        states = table["state_fips"].astype(str)
        loo = {}
        for s in sorted(states.unique()):
            keep = states != s
            r = st._fit(table.loc[keep], counts.loc[keep], nights.loc[keep], (PALEOZOIC, *full)).coefficients.loc[PALEOZOIC]
            loo[s] = r
        rr = pd.Series({s: r["rate_ratio"] for s, r in loo.items()})
        ps = pd.Series({s: r["p_value"] for s, r in loo.items()})
        lines += ["", "## Leave one state out (full model)", "",
                  f"Rate ratio ranges {rr.min():.3f} (without {STATE_NAMES.get(rr.idxmin(), rr.idxmin())}) to "
                  f"{rr.max():.3f} (without {STATE_NAMES.get(rr.idxmax(), rr.idxmax())}); p < 0.05 in "
                  f"{int((ps < 0.05).sum())} of {len(ps)} fits; largest p {ps.max():.3g} "
                  f"(without {STATE_NAMES.get(ps.idxmax(), ps.idxmax())}). FIPS codes: lowest {rr.idxmin()}, highest {rr.idxmax()}."]

        # Shift test: move the geologic map (Paleozoic and sediment-cover shares together); land cover stays put.
        p = st.p
        rng = np.random.default_rng(p["seed"])
        cen = st.counties.union_all().centroid
        observed = float(np.log(coef.loc[PALEOZOIC, "rate_ratio"]))
        null = []
        for trial in range(p["shift_trials"]):
            angle = rng.uniform(-p["max_rotate_deg"], p["max_rotate_deg"])
            dx, dy = rng.uniform(-p["max_shift_km"] * M_PER_KM, p["max_shift_km"] * M_PER_KM, size=2)
            moved = summary.summarize(summary.grid.shifted(angle, dx, dy, (cen.x, cen.y))).reindex(table.index)
            alt = table.assign(**{PALEOZOIC: moved[PALEOZOIC],
                                  "share_unconsolidated_all": moved[[f"share_{e}_unconsolidated" for e in ERA_NAMES]].sum(axis=1)})
            try:
                null.append(float(np.log(st._fit(alt, counts, nights, (PALEOZOIC, *full)).coefficients.loc[PALEOZOIC, "rate_ratio"])))
            except Exception:  # noqa: BLE001 - a degenerate copy is skipped and counted
                pass
        null = np.asarray(null)
        q = np.exp(np.quantile(null, [0.025, 0.5, 0.975])) if len(null) else [np.nan] * 3
        lines += ["", "## Shift test (full model)", "",
                  f"Real map {np.exp(observed):.3f}; {len(null)} shifted copies fitted, rate ratios {q[0]:.3f} (2.5%), "
                  f"{q[1]:.3f} (median), {q[2]:.3f} (97.5%); two-sided p {two_sided_shift_p(observed, null):.3f}."]

        out = st.root / "results" / st.HYPOTHESIS_ID / "diagnostics"
        out.mkdir(parents=True, exist_ok=True)
        path = out / "land_use.md"
        path.write_text("\n".join(lines) + "\n")
        return path
