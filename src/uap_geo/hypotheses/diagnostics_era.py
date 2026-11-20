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

from uap_geo.common.geo import COUNTY_ID

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
