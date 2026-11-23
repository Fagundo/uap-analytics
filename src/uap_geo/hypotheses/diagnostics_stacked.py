"""Post hoc: one geology model over every catalog, each compared only within itself.

Question: is the Paleozoic (and carbonate) association one effect across catalogs and decades, or a feature of
the NUFORC era? Exploratory, descriptive, not registered.

Data: county x decade x catalog rows (NUFORC, Hatch, NICAP, Blue Book index and unknowns together), 1950-2023,
selected as in the combined run (contiguous U.S., site or town level, not a hoax, NUFORC repeat or explained).
A case found in several catalogs is counted once, under the source closest to the original report: PURSUE's
government documents, then Blue Book, then NUFORC (first-hand reports), then the compilations NICAP, Hatch,
Magonia. Catalog-decade strata with fewer than ``MIN_STRATUM`` records are left out (Magonia and PURSUE's
incidents have too few to form any).

Model: Poisson pseudo-maximum likelihood (ppmlhdfe, via pyfixest) with catalog x state x decade fixed effects,
so every comparison is between counties of one state, in one decade, as one catalog saw them. The exposure is
the county's population at the decade's census x years; it enters as Poisson weights on the rate (the same
estimating equations as a log-exposure offset). Controls: the H-persist-01 set (today's values). Standard
errors clustered by state. Shares and controls are standardized over counties (rate ratio per SD).

Two weightings:
  natural   every record counts once (NUFORC carries most of the weight)
  balanced  every catalog-decade stratum carries the same total weight, however many records it has
Plus: the slope before and from 1980 (interaction), NUFORC against Hatch where both cover the same decades,
and every stratum's own estimate with a random-effects meta-analysis across them (I^2: how much the strata
disagree beyond chance).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from uap_geo.common.geo import COUNTY_ID
from uap_geo.hypotheses.diagnostics_combined import (
    EXPOSURES,
    LAST_YEAR,
    CombinedPanelDiagnostics,
)

CATALOGS = {"nuforc": "NUFORC", "hatch": "Hatch", "nicap": "NICAP", "bluebook-index": "Blue Book",
            "bluebook-unknowns": "Blue Book"}
PRIORITY = ["pursue", "bluebook-unknowns", "bluebook-index", "nuforc", "nicap", "hatch", "magonia"]
MIN_STRATUM = 100
MODERN_FROM = 1980
Z = 1.959964


def one_per_case(rows: pd.DataFrame) -> pd.DataFrame:
    """Records not linked to another catalog, plus one per cross-source group: the first-hand source's."""
    rank = rows["source"].map({s: i for i, s in enumerate(PRIORITY)}).fillna(len(PRIORITY))
    r = rows.assign(_rank=rank).sort_values(["_rank", "sighting_id"])
    grouped = r["dedup_group"].notna()
    return pd.concat([r.loc[~grouped], r.loc[grouped].drop_duplicates("dedup_group")]).drop(columns="_rank")


def stack(table: pd.DataFrame, pop: pd.DataFrame, records: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """County x decade x catalog rows for strata with at least MIN_STRATUM records: count, exposure
    (person-years / 1e5), rate, the standardized columns, and the fixed-effect and stratum keys."""
    rec = records.loc[records["source"].isin(CATALOGS)].assign(
        catalog=lambda d: d["source"].map(CATALOGS), decade=lambda d: (d["date"].dt.year // 10) * 10)
    sizes = rec.groupby(["catalog", "decade"]).size()
    z = (table[columns] - table[columns].mean()) / table[columns].std(ddof=0)
    parts = []
    for (catalog, decade), n in sizes.items():
        if n < MIN_STRATUM:
            continue
        years = min(decade + 9, LAST_YEAR) - decade + 1
        counts = rec.loc[(rec["catalog"] == catalog) & (rec["decade"] == decade)].groupby(COUNTY_ID).size()
        part = z.copy()
        part["count"] = counts.reindex(table.index, fill_value=0).to_numpy()
        part["exposure"] = pop[decade].to_numpy() * years / 1e5
        part["state_fips"] = table["state_fips"].astype(str).to_numpy()
        part["catalog"], part["decade"] = catalog, decade
        parts.append(part.reset_index())
    out = pd.concat(parts, ignore_index=True)
    out["rate"] = out["count"] / out["exposure"]
    out["cell"] = out["catalog"] + "_" + out["state_fips"] + "_" + out["decade"].astype(str)
    out["stratum"] = out["catalog"] + " " + out["decade"].astype(str) + "s"
    out["modern"] = (out["decade"] >= MODERN_FROM).astype(float)
    out["is_nuforc"] = (out["catalog"] == "NUFORC").astype(float)
    sums = out.groupby("stratum")["count"].transform("sum")
    out["w_natural"] = out["exposure"]
    out["w_balanced"] = out["exposure"] * sums.groupby(out["stratum"]).first().mean() / sums
    return out.dropna(subset=columns)


class PpmlFit:
    """Rate ratios (per SD) from pyfixest's fepois on the rate with exposure weights."""

    def __init__(self, data: pd.DataFrame, terms: list[str], controls: list[str], fe: str, weights: str):
        import pyfixest as pf

        rhs = " + ".join([*terms, *controls])
        self.fit = pf.fepois(f"rate ~ {rhs} | {fe}", data=data, weights=weights, vcov={"CRV1": "state_fips"})
        self.n = int(self.fit._N)

    def row(self, name: str) -> dict:
        b, se, p = float(self.fit.coef()[name]), float(self.fit.se()[name]), float(self.fit.pvalue()[name])
        return {"log_rr": b, "se": se, "rate_ratio": np.exp(b), "ci_low": np.exp(b - Z * se),
                "ci_high": np.exp(b + Z * se), "p_value": p}

    def combined(self, a: str, b: str) -> dict:
        """exp(beta_a + beta_b) with its CI (the slope in the group the interaction b switches on)."""
        v = self.fit._vcov
        names = list(self.fit.coef().index)
        i, j = names.index(a), names.index(b)
        est = float(self.fit.coef()[a] + self.fit.coef()[b])
        se = float(np.sqrt(v[i, i] + v[j, j] + 2 * v[i, j]))
        from scipy.stats import norm
        return {"log_rr": est, "se": se, "rate_ratio": np.exp(est), "ci_low": np.exp(est - Z * se),
                "ci_high": np.exp(est + Z * se), "p_value": float(2 * norm.sf(abs(est / se)))}


def meta(estimates: pd.DataFrame) -> dict:
    """Fixed-effect (inverse variance), DerSimonian-Laird random-effects and equal-weight pooling of log rate
    ratios; Cochran's Q and I^2."""
    from scipy.stats import chi2, norm

    y, v = estimates["log_rr"].to_numpy(), estimates["se"].to_numpy() ** 2
    w = 1 / v
    fe = float(np.sum(w * y) / np.sum(w))
    q = float(np.sum(w * (y - fe) ** 2))
    k = len(y)
    tau2 = max(0.0, (q - (k - 1)) / (np.sum(w) - np.sum(w**2) / np.sum(w)))
    wr = 1 / (v + tau2)
    re = float(np.sum(wr * y) / np.sum(wr))
    out = {"k": k, "Q": q, "Q_p": float(chi2.sf(q, k - 1)), "I2": max(0.0, (q - (k - 1)) / q) if q > 0 else 0.0,
           "tau": float(np.sqrt(tau2))}
    for name, est, se in (("fixed effect", fe, np.sqrt(1 / np.sum(w))), ("random effects", re, np.sqrt(1 / np.sum(wr))),
                          ("equal weight", float(y.mean()), float(np.sqrt(np.sum(v + tau2)) / k))):
        out[name] = {"rate_ratio": np.exp(est), "ci_low": np.exp(est - Z * se), "ci_high": np.exp(est + Z * se),
                     "p_value": float(2 * norm.sf(abs(est / se)))}
    return out


class StackedCatalogDiagnostics(CombinedPanelDiagnostics):
    def run(self) -> Path:
        st = self.study
        table, pop, rows, steps = self.inputs()
        cases = one_per_case(rows)
        controls = list(st.controls)
        data = stack(table, pop, cases, [*EXPOSURES, *controls])
        for x in EXPOSURES:
            data[f"{x}_modern"] = data[x] * data["modern"]
            data[f"{x}_nuforc"] = data[x] * data["is_nuforc"]

        f = lambda r: f"{r['rate_ratio']:.3f} ({r['ci_low']:.3f}–{r['ci_high']:.3f})"
        stars = lambda p: "**" if p < 0.01 else ("*" if p < 0.05 else "")
        cell = lambda r: f"{f(r)}{stars(r['p_value'])}"
        strata = data.groupby("stratum").agg(records=("count", "sum"), catalog=("catalog", "first"),
                                             decade=("decade", "first")).sort_values(["catalog", "decade"])
        lines = ["# Post hoc: one geology model over every catalog, each compared within itself", "",
                 __doc__.split("\n\n", 1)[1].strip(), "", "## Records", "", "| Step | Records |", "| --- | --- |"]
        lines += [f"| {k} | {v:,} |" for k, v in steps.items()]
        lines += [f"| one per case (first-hand source kept) | {len(cases):,} |",
                  f"| in the stacked model (strata of {MIN_STRATUM}+ records) | {int(data['count'].sum()):,} |",
                  "", "Strata: " + ", ".join(f"{s} {int(r.records):,}" for s, r in strata.iterrows()) + ".", "",
                  "Rate ratio per SD (95% CI); * p < 0.05, ** p < 0.01.", ""]

        for x, label in EXPOSURES.items():
            lines += [f"## {label}", "", "| Model | Rate ratio per SD |", "| --- | --- |"]
            for w in ("natural", "balanced"):
                lines.append(f"| All strata, {w} weighting | {cell(PpmlFit(data, [x], controls, 'cell', f'w_{w}').row(x))} |")
            era = PpmlFit(data, [x, f"{x}_modern"], controls, "cell", "w_natural")
            inter = era.row(f"{x}_modern")
            lines += [f"| Before {MODERN_FROM} (all catalogs) | {cell(era.row(x))} |",
                      f"| From {MODERN_FROM} (all catalogs) | {cell(era.combined(x, f'{x}_modern'))} |",
                      f"| Difference, from {MODERN_FROM} vs before (ratio of ratios) | {cell(inter)} |"]
            both = data.loc[data["catalog"].isin(["NUFORC", "Hatch"]) & data["decade"].between(1950, 1990)]
            both = both.loc[both.groupby("cell")["catalog"].transform("size") > 0]
            shared = set(both.loc[both["catalog"] == "NUFORC", "decade"]) & set(both.loc[both["catalog"] == "Hatch", "decade"])
            both = both.loc[both["decade"].isin(shared)]
            if shared:
                ov = PpmlFit(both, [x, f"{x}_nuforc"], controls, "cell", "w_natural")
                lines += [f"| Same decades ({', '.join(f'{d}s' for d in sorted(shared))}): Hatch | {cell(ov.row(x))} |",
                          f"| Same decades: NUFORC | {cell(ov.combined(x, f'{x}_nuforc'))} |",
                          f"| Same decades: NUFORC vs Hatch (ratio of ratios) | {cell(ov.row(f'{x}_nuforc'))} |"]
            est = {}
            for s in strata.index:
                part = data.loc[data["stratum"] == s]
                try:
                    est[s] = PpmlFit(part, [x], controls, "state_fips", "w_natural").row(x)
                except Exception as exc:  # noqa: BLE001 - a stratum too thin to fit
                    est[s] = {"error": type(exc).__name__}
            ok = pd.DataFrame({s: r for s, r in est.items() if "error" not in r}).T
            m = meta(ok)
            het = (f"Heterogeneity across strata: Q {m['Q']:.1f} on {m['k'] - 1} df (p {m['Q_p']:.3g}), "
                   f"I² {m['I2']:.0%}, tau {m['tau']:.3f} (log rate ratio).")
            lines += [f"| Meta-analysis over {m['k']} strata: fixed effect | {cell(m['fixed effect'])} |",
                      f"| Meta-analysis: random effects | {cell(m['random effects'])} |",
                      f"| Meta-analysis: equal weight per stratum | {cell(m['equal weight'])} |", "", het, "",
                      "| Stratum | Records | Rate ratio per SD (state FE) |", "| --- | --- | --- |"]
            for s in strata.index:
                r = est[s]
                lines.append(f"| {s} | {int(strata.loc[s, 'records']):,} | "
                             + (cell(r) if "error" not in r else f"not fitted ({r['error']})") + " |")
            lines.append("")
        lines.append("Descriptive and post hoc. Counts describe reporting and collection, not phenomena. Controls are "
                     "today's values; Blue Book's index and unknowns are one catalog here.")
        out = st.root / "results" / "H-hatchpal-01" / "diagnostics"
        out.mkdir(parents=True, exist_ok=True)
        path = out / "stacked_catalogs.md"
        path.write_text("\n".join(lines) + "\n")
        return path
