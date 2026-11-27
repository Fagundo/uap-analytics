"""H-rocktype-01: which rock types at the surface, if any, go with how many UAP events a county reports,
beyond the observer controls?

A screen of all seven rock-type classes (features/rock_type.py), each tested on its own as the county's
share of that class (per SD, two-sided), with Benjamini-Hochberg correction across the seven. A class is
confirmed only if its corrected p < 0.05 and the real map beats rigidly shifted copies of itself.
"""

from __future__ import annotations

import gc
import logging

import numpy as np
import pandas as pd

from uap_analytics.common.geo import COUNTY_ID, M_PER_KM
from uap_analytics.features.rock_type import CLASS_LABELS, CLASSES, CountyTypeSummary, UnitGrid, build_unit_grid, unit_class_weights
from uap_analytics.hypotheses.base import TestOutcome
from uap_analytics.hypotheses.county_period import CountyPeriodStudy
from uap_analytics.hypotheses.designs.conditional_poisson import TestResult
from uap_analytics.hypotheses.event_table import EventTable
from uap_analytics.hypotheses.rock_age import two_sided_shift_p
from uap_analytics.evaluation.stats_utils import benjamini_hochberg

log = logging.getLogger(__name__)
GRID_VERSION = "v1"   # bump when the rasterization changes, so a cached grid is not reused


def term(name: str) -> str:
    return f"share_{name}"


class RockTypeStudy(CountyPeriodStudy):
    HYPOTHESIS_ID = "H-rocktype-01"
    PARAM_KEY = "rock_type"
    MODEL_NAME = "rock_type"
    TEST_LABELS = {c: f"{CLASS_LABELS[c]} (share, per SD)" for c in CLASSES}
    CHECK_LABELS = {"shift_test": "Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05)"}

    # ------------------------------------------------------------------------------ inputs
    def _type_summary(self, weights: pd.DataFrame | None = None) -> CountyTypeSummary:
        """County summary for the given unit weights (default: the seven rock-type classes)."""
        source = self.sources.geologic_map()
        if weights is None:
            weights = unit_class_weights(source.lithology_table())
        counties = self.counties[[COUNTY_ID, "geometry"]].reset_index(drop=True)
        counties["county_index"] = np.arange(len(counties), dtype="int32")
        cache = self.config.paths.raw / "sgmc" / f"unit_grid_{GRID_VERSION}_{float(self.p['cell_km']):g}km_{len(counties)}.npz"
        if cache.exists():
            grid = UnitGrid.load(cache)
            log.info("Unit grid loaded from %s", cache)
        else:
            geology = source.load()[["unit_link", "geometry"]].to_crs(self.counties.crs)
            grid = build_unit_grid(geology, counties, float(self.p["cell_km"]) * M_PER_KM)
            del geology
            gc.collect()
            grid.save(cache)
        summary = CountyTypeSummary(grid, weights, counties[COUNTY_ID].to_numpy(),
                                    *(lambda c: (c.x.to_numpy(), c.y.to_numpy()))(counties.geometry.centroid))
        in_county = grid.county >= 0
        mapped = in_county & (grid.unit >= 0)
        self.coverage = {"map units with a rock type": int(summary.classified.sum()),
                         "share of county cells on a classified unit": float((mapped & np.isin(
                             grid.unit, np.flatnonzero(summary.classified))).sum() / max(in_county.sum(), 1))}
        log.info("Rock-type grid %s; %s", grid.shape, self.coverage)
        return summary

    # ------------------------------------------------------------------------------ shift test
    def _shift_test(self, summary: CountyTypeSummary, table: pd.DataFrame, counts: pd.Series, nights: pd.Series,
                    observed: dict[str, float]) -> dict[str, dict]:
        rng = np.random.default_rng(self.p["seed"])
        c = self.counties.union_all().centroid
        null = {k: [] for k in CLASSES}
        for trial in range(self.p["shift_trials"]):
            angle = rng.uniform(-self.p["max_rotate_deg"], self.p["max_rotate_deg"])
            dx, dy = rng.uniform(-self.p["max_shift_km"] * M_PER_KM, self.p["max_shift_km"] * M_PER_KM, size=2)
            moved = summary.summarize(summary.grid.shifted(angle, dx, dy, (c.x, c.y))).reindex(table.index)
            for k in CLASSES:
                try:
                    fit = self._fit(table.assign(**{term(k): moved[term(k)]}), counts, nights, (term(k),))
                    null[k].append(float(np.log(fit.coefficients.loc[term(k), "rate_ratio"])))
                except Exception as exc:  # a degenerate copy is skipped and counted in the report
                    log.warning("Shift trial %d, %s failed: %s", trial, k, exc)
            if (trial + 1) % 25 == 0:
                log.info("Shift test: %d/%d", trial + 1, self.p["shift_trials"])
        self.shift_null = {k: np.asarray(v) for k, v in null.items()}
        out = {}
        for k in CLASSES:
            p_shift = two_sided_shift_p(observed[k], self.shift_null[k])
            out[k] = {"rate_ratio": float(np.exp(observed[k])), "p_value": p_shift,
                      "n_events": int(len(self.shift_null[k])), "holds": bool(p_shift < 0.05)}
        return out

    # ------------------------------------------------------------------------------ analysis
    def analyse(self) -> tuple[EventTable, list[TestOutcome]]:
        table = self._county_table()
        events_table = EventTable(self.config, self.sources, self.filters, self.impl, self._all_years(),
                                  tuple(self.spec.get("filters_disabled") or ()))
        events = events_table.build(None, self.counties)
        events["night"] = pd.DatetimeIndex(events["night"]).as_unit("ns")
        removed = self._removed_launch_nights(table)

        summary = self._type_summary()
        types = summary.summarize()
        table = table.join(types[[term(k) for k in CLASSES]])
        self.coverage["counties with a rock type"] = int(table[term(CLASSES[0])].notna().sum())
        self.class_means = {k: float(table[term(k)].mean()) for k in CLASSES}

        years = self._split_years()
        outcomes = {k: TestOutcome(k) for k in CLASSES}
        observed = {}
        for tier in self.TIERS:
            counts, _, nights = self._period_counts(events, removed, years, table.index, tier)
            for k in CLASSES:
                fit = self._fit(table, counts, nights, (term(k),))
                row = fit.coefficients.loc[[term(k)]].rename(index={term(k): "exposed"})
                outcomes[k].by_tier[tier] = TestResult(row, fit.n, int(counts.sum()), float("nan"))
                if tier == self.PRIMARY:
                    observed[k] = float(np.log(fit.coefficients.loc[term(k), "rate_ratio"]))
            if tier == self.PRIMARY:
                primary = (counts, nights)
        counts, nights = primary
        checks = self._shift_test(summary, table, counts, nights, observed)
        alpha = self.impl["parameters"]["power"]["alpha"] / len(CLASSES)   # Bonferroni: conservative for BH
        for k in CLASSES:
            outcomes[k].checks = {"shift_test": checks[k]}
            outcomes[k].power = self._power_from_explore(table, events, removed, int(counts.sum()), term(k),
                                                         two_sided=True, scale=False, alpha=alpha)
        self.type_rows = self._by_type(table, counts, nights, types)
        return events_table, [outcomes[k] for k in CLASSES]

    def _by_type(self, table, counts, nights, types) -> list[dict]:
        """Descriptive: observed / expected events by the county's dominant rock type (controls-only model)."""
        fit = self._fit(table, counts, nights)
        expected = fit.fitted
        observed = counts.reindex(expected.index)
        dom = types["dominant_type"].reindex(expected.index)
        return [{"type": k, "counties": int((dom == k).sum()), "observed": int(observed[dom == k].sum()),
                 "expected": float(expected[dom == k].sum())} for k in CLASSES]

    # ------------------------------------------------------------------------------ verdicts (two-sided, BH)
    def _verdicts(self, outcomes: list[TestOutcome]) -> None:
        p = self.impl["parameters"]["power"]
        adjusted = benjamini_hochberg(pd.Series([o.by_tier[self.PRIMARY].p_value() for o in outcomes])).to_numpy()
        for o, q in zip(outcomes, adjusted):
            o.p_bh = float(q)
            if self.split == "explore":
                o.verdict = "exploration (no verdict)"
                continue
            main = o.by_tier[self.PRIMARY].terms.loc["exposed"]
            soi = p["rate_ratio"]
            if o.p_bh < 0.05 and o.checks["shift_test"]["holds"]:
                o.verdict = "confirmed (more reports)" if main["rate_ratio"] > 1 else "confirmed (fewer reports)"
            elif o.power < p["underpowered_below"]:
                o.verdict = "underpowered"
            elif o.power >= p["refute_requires"] and main["ci_low"] > 1 / soi and main["ci_high"] < soi:
                o.verdict = "refuted"
            else:
                o.verdict = "inconclusive"

    # ------------------------------------------------------------------------------ report
    def extra_report_lines(self) -> list[str]:
        lines = []
        if getattr(self, "class_means", None):
            lines += ["## Rock-type classes", "", "Classes come from each map unit's major lithologies (SGMC "
                      "Lithology table, LITH1 and LITH2); a unit with several is split evenly.", "",
                      "| Class | Mean county share |", "| --- | --- |"]
            lines += [f"| {CLASS_LABELS[k]} | {v:.1%} |" for k, v in self.class_means.items()]
            lines.append("")
        if getattr(self, "type_rows", None):
            lines += ["## Observed and expected events by dominant rock type (primary tier)", "",
                      "Expected counts come from the controls-only model; descriptive.", "",
                      "| Dominant type | Counties | Observed | Expected | Ratio |", "| --- | --- | --- | --- | --- |"]
            for r in self.type_rows:
                ratio = r["observed"] / r["expected"] if r["expected"] else float("nan")
                lines.append(f"| {r['type']} | {r['counties']:,} | {r['observed']:,} | {r['expected']:,.0f} | {ratio:.2f} |")
            lines.append("")
        null = getattr(self, "shift_null", None)
        if null:
            lines += ["## Shift-test copies (primary tier)", "", "| Class | Copies fitted | 2.5% | Median | 97.5% |",
                      "| --- | --- | --- | --- | --- |"]
            for k, v in null.items():
                if len(v):
                    q = np.exp(np.quantile(v, [0.025, 0.5, 0.975]))
                    lines.append(f"| {k} | {len(v)} | {q[0]:.3f} | {q[1]:.3f} | {q[2]:.3f} |")
            lines.append("")
        lines.append("Power: two-sided for rate ratio 1.10 or 1/1.10 at alpha 0.05/7, from the explore-period "
                     "standard error of each share, not scaled down for more events.")
        if getattr(self, "coverage", None):
            lines += ["", "; ".join(f"{k}: {v:,.3g}" if isinstance(v, float) else f"{k}: {v:,}"
                                    for k, v in self.coverage.items()) + "."]
        return lines
