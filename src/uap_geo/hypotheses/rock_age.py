"""H-rockage-01: does the geologic age of the rocks at the surface go with how many UAP events a county
reports, beyond the observer controls?

The exposure is the county's mean log10 age (Ma) of the mapped units at the surface (USGS State Geologic
Map Compilation, rasterized at 1 km). No direction is predicted: tectonic-strain ideas point to young,
active terrain, crystalline-basement ideas to old rock. The test is two-sided, and the layer-shift test
asks whether the real map beats rigidly rotated and shifted copies of itself in absolute effect.
Era shares (Mesozoic, Paleozoic, Precambrian against Cenozoic) are reported as secondary estimates.
"""

from __future__ import annotations

import gc
import logging

import numpy as np
import pandas as pd

from uap_geo.common.geo import COUNTY_ID, M_PER_KM
from uap_geo.features.rock_age import ERA_NAMES, CountyAgeSummary, build_age_grid
from uap_geo.hypotheses.base import TestOutcome
from uap_geo.hypotheses.county_period import CountyPeriodStudy
from uap_geo.hypotheses.designs.conditional_poisson import TestResult
from uap_geo.hypotheses.event_table import EventTable

log = logging.getLogger(__name__)
TERM = "rock_log10_age"
ERA_TERMS = tuple(f"share_{n}" for n in ERA_NAMES[1:])     # Cenozoic is the reference


def two_sided_shift_p(observed: float, null: np.ndarray) -> float:
    """(1 + copies whose |log rate ratio| >= observed's) / (1 + copies)."""
    null = np.asarray(null, dtype=float)
    return float((1 + np.sum(np.abs(null) >= abs(observed))) / (1 + len(null)))


class RockAgeStudy(CountyPeriodStudy):
    HYPOTHESIS_ID = "H-rockage-01"
    PARAM_KEY = "rock_age"
    MODEL_NAME = "rock_age"
    TEST_LABELS = {"age": "Mean geologic age of surface rock, log10 Ma (per SD; two-sided)"}
    CHECK_LABELS = {"shift_test": "Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05)"}

    # ------------------------------------------------------------------------------ inputs
    def _age_summary(self) -> CountyAgeSummary:
        geology = self.sources.geologic_map().load()
        geology = geology[["log10_age", "geometry"]].to_crs(self.counties.crs)
        counties = self.counties[[COUNTY_ID, "geometry"]].reset_index(drop=True)
        counties["county_index"] = np.arange(len(counties), dtype="int32")
        grid = build_age_grid(geology, counties, float(self.p["cell_km"]) * M_PER_KM)
        del geology
        gc.collect()
        dated = np.isfinite(grid.log_age) & (grid.county >= 0)
        log.info("Age grid %s cells; %.1f%% of county cells dated", grid.shape, 100 * dated.sum() / max((grid.county >= 0).sum(), 1))
        cent = counties.geometry.centroid
        return CountyAgeSummary(grid, counties[COUNTY_ID].to_numpy(), cent.x.to_numpy(), cent.y.to_numpy())

    # ------------------------------------------------------------------------------ shift test
    def _shift_test(self, summary: CountyAgeSummary, table: pd.DataFrame, counts: pd.Series, nights: pd.Series,
                    observed_log_rr: float) -> dict:
        rng = np.random.default_rng(self.p["seed"])
        c = self.counties.union_all().centroid
        origin = (c.x, c.y)
        null = []
        for trial in range(self.p["shift_trials"]):
            angle = rng.uniform(-self.p["max_rotate_deg"], self.p["max_rotate_deg"])
            dx, dy = rng.uniform(-self.p["max_shift_km"] * M_PER_KM, self.p["max_shift_km"] * M_PER_KM, size=2)
            log_age, era = summary.grid.shifted(angle, dx, dy, origin)
            moved = summary.summarize(log_age, era)[TERM].reindex(table.index)
            try:
                fit = self._fit(table.assign(**{TERM: moved}), counts, nights, (TERM,))
                null.append(float(np.log(fit.coefficients.loc[TERM, "rate_ratio"])))
            except Exception as exc:  # a degenerate copy is skipped and counted in the report
                log.warning("Shift trial %d failed: %s", trial, exc)
            if (trial + 1) % 50 == 0:
                log.info("Shift test: %d/%d", trial + 1, self.p["shift_trials"])
        null = np.asarray(null)
        p_shift = two_sided_shift_p(observed_log_rr, null)
        self.shift_null = null
        return {"rate_ratio": float(np.exp(observed_log_rr)), "p_value": p_shift, "n_events": int(len(null)),
                "null_median_rate_ratio": float(np.exp(np.median(null))) if len(null) else float("nan"),
                "holds": bool(p_shift < 0.05)}

    # ------------------------------------------------------------------------------ analysis
    def analyse(self) -> tuple[EventTable, list[TestOutcome]]:
        table = self._county_table()
        events_table = EventTable(self.config, self.sources, self.filters, self.impl, self._all_years(),
                                  tuple(self.spec.get("filters_disabled") or ()))
        events = events_table.build(None, self.counties)
        events["night"] = pd.DatetimeIndex(events["night"]).as_unit("ns")
        removed = self._removed_launch_nights(table)

        summary = self._age_summary()
        ages = summary.summarize()
        table = table.join(ages[[TERM, *[f"share_{n}" for n in ERA_NAMES]]])
        self.coverage = {"counties": len(table), "counties with a dated surface unit": int(table[TERM].notna().sum()),
                         "counties from the centroid cell (smaller than a cell)": int(summary._needs_fallback.sum())}

        o = TestOutcome("age")
        years = self._split_years()
        self.secondary = {}
        for tier in self.TIERS:
            counts, _, nights = self._period_counts(events, removed, years, table.index, tier)
            fit = self._fit(table, counts, nights, (TERM,))
            row = fit.coefficients.loc[[TERM]].rename(index={TERM: "exposed"})
            o.by_tier[tier] = TestResult(row, fit.n, int(counts.sum()), float("nan"))
            if tier != self.PRIMARY:
                continue
            log_rr = float(np.log(fit.coefficients.loc[TERM, "rate_ratio"]))
            o.checks = {"shift_test": self._shift_test(summary, table, counts, nights, log_rr)}
            o.power = self._power_from_explore(table, events, removed, int(counts.sum()), TERM, two_sided=True)
            eras = self._fit(table, counts, nights, ERA_TERMS).coefficients
            for term in ERA_TERMS:
                self.secondary[f"{term.replace('share_', '').title()} share (vs Cenozoic), per SD"] = eras.loc[term].to_dict()
            self.era_rows = self._by_era(table, counts, nights, ages)
        return events_table, [o]

    def _by_era(self, table, counts, nights, ages) -> list[dict]:
        """Descriptive: observed / expected events by the county's dominant era, from the controls-only model."""
        fit = self._fit(table, counts, nights)
        expected = fit.fitted
        observed = counts.reindex(expected.index)
        era = ages["dominant_era"].reindex(expected.index)
        rows = []
        for name in ERA_NAMES:
            m = era == name
            rows.append({"era": name.title(), "counties": int(m.sum()), "observed": int(observed[m].sum()),
                         "expected": float(expected[m].sum())})
        return rows

    # ------------------------------------------------------------------------------ verdicts (two-sided)
    def _verdicts(self, outcomes: list[TestOutcome]) -> None:
        p = self.impl["parameters"]["power"]
        for o in outcomes:
            o.p_bh = o.by_tier[self.PRIMARY].p_value()   # one primary test: no adjustment
            if self.split == "explore":
                o.verdict = "exploration (no verdict)"
                continue
            main = o.by_tier[self.PRIMARY].terms.loc["exposed"]
            soi = p["rate_ratio"]
            if o.p_bh < 0.05 and o.checks["shift_test"]["holds"]:
                o.verdict = "confirmed (older rock, more reports)" if main["rate_ratio"] > 1 else \
                    "confirmed (younger rock, more reports)"
            elif o.power < p["underpowered_below"]:
                o.verdict = "underpowered"
            elif o.power >= p["refute_requires"] and main["ci_low"] > 1 / soi and main["ci_high"] < soi:
                o.verdict = "refuted"
            else:
                o.verdict = "inconclusive"

    # ------------------------------------------------------------------------------ report
    def extra_report_lines(self) -> list[str]:
        lines = []
        if getattr(self, "secondary", None):
            lines += ["## Secondary estimates: era shares (primary tier)", "",
                      "One model with the Mesozoic, Paleozoic and Precambrian shares of each county's dated cells "
                      "(Cenozoic is the reference). Descriptive; no verdict.", "",
                      "| Term | Rate ratio | 95% CI | p |", "| --- | --- | --- | --- |"]
            for name, r in self.secondary.items():
                lines.append(f"| {name} | {r['rate_ratio']:.3f} | {r['ci_low']:.3f}–{r['ci_high']:.3f} | {r['p_value']:.3g} |")
            lines.append("")
        if getattr(self, "era_rows", None):
            lines += ["## Observed and expected events by dominant era (primary tier)", "",
                      "Expected counts come from the controls-only model; descriptive.", "",
                      "| Dominant era | Counties | Observed | Expected | Ratio |", "| --- | --- | --- | --- | --- |"]
            for r in self.era_rows:
                ratio = r["observed"] / r["expected"] if r["expected"] else float("nan")
                lines.append(f"| {r['era']} | {r['counties']:,} | {r['observed']:,} | {r['expected']:,.0f} | {ratio:.2f} |")
            lines.append("")
        null = getattr(self, "shift_null", None)
        if null is not None and len(null):
            q = np.exp(np.quantile(null, [0.025, 0.5, 0.975]))
            lines += [f"Shift test: {len(null)} of {self.p['shift_trials']} copies fitted; their rate ratios run "
                      f"{q[0]:.3f} (2.5%), {q[1]:.3f} (median), {q[2]:.3f} (97.5%).", ""]
        if getattr(self, "power_inputs", None):
            pi = self.power_inputs
            lines.append(f"Power inputs: explore SE {pi['se_explore']:.4f} on {pi['events_explore']:,} events; "
                         f"this split {pi['events_split']:,} events, SE {pi['se_split']:.4f}.")
        if getattr(self, "coverage", None):
            lines += ["", "; ".join(f"{k}: {v:,}" for k, v in self.coverage.items()) + "."]
        return lines
