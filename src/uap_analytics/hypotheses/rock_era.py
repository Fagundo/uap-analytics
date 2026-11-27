"""H-rockera-01 (post hoc): geologic era as the class, and era crossed with rock type.

Asks whether the Paleozoic lead (H-rockage-01 secondary) is about age or about rock type (carbonate,
H-rocktype-01). Every split of the data has already been seen, so this is a labelled post-hoc analysis:
one run on 2001-2023 pooled, per-period estimates for consistency, the layer-shift test that the Paleozoic
estimate never had, and joint models that put era and rock type against each other. No verdicts.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from uap_analytics.common.geo import M_PER_KM
from uap_analytics.data.scraping.sgmc import unit_ages
from uap_analytics.features.rock_age import ERA_NAMES, era_codes
from uap_analytics.features.rock_type import CLASSES as TYPES, unit_class_weights
from uap_analytics.hypotheses.base import TestOutcome
from uap_analytics.hypotheses.designs.conditional_poisson import TestResult
from uap_analytics.hypotheses.event_table import EventTable
from uap_analytics.hypotheses.rock_age import two_sided_shift_p
from uap_analytics.hypotheses.rock_type import RockTypeStudy, term
from uap_analytics.evaluation.stats_utils import benjamini_hochberg

log = logging.getLogger(__name__)
PERIODS = {"2001–2010": (2001, 2010), "2011–2020": (2011, 2020), "2021–2023": (2021, 2023)}


def era_type_weights(type_weights: pd.DataFrame, ages: pd.DataFrame) -> pd.DataFrame:
    """Per unit: era one-hot (by midpoint age) and era x type weights (type weight within the unit's era).
    Only units with both an age and a rock type are kept."""
    era = pd.Series(era_codes(ages["mid_ma"].to_numpy()), index=ages["unit_link"].astype(str))
    era = era[era >= 0]
    units = type_weights.index.intersection(era.index)
    tw, code = type_weights.loc[units], era.loc[units].to_numpy()
    cols = {}
    for k, e in enumerate(ERA_NAMES):
        cols[e] = (code == k).astype(float)
    for k, e in enumerate(ERA_NAMES):
        for t in TYPES:
            cols[f"{e}_{t}"] = np.where(code == k, tw[t].to_numpy(), 0.0)
    return pd.DataFrame(cols, index=units)


class RockEraStudy(RockTypeStudy):
    HYPOTHESIS_ID = "H-rockera-01"
    PARAM_KEY = "rock_era"
    MODEL_NAME = "rock_era"
    TEST_LABELS: dict[str, str] = {}
    CHECK_LABELS = {"shift_test": "Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05)"}

    # ------------------------------------------------------------------------------ classes
    def _weights(self) -> pd.DataFrame:
        source = self.sources.geologic_map()
        types = unit_class_weights(source.lithology_table())
        ages = unit_ages(source.age_table())
        return era_type_weights(types, ages)

    def _select_classes(self, shares: pd.DataFrame) -> list[str]:
        """Eras, plus era x type crosses whose mean county share reaches min_cross_share (map only, no reports)."""
        keep = list(ERA_NAMES)
        for c in shares.columns.str.replace("share_", ""):
            if c not in ERA_NAMES and shares[term(c)].mean() >= self.p["min_cross_share"]:
                keep.append(c)
        return keep

    # ------------------------------------------------------------------------------ analysis
    def prepare(self):
        """County table with era and era x type shares, events, removed nights, the grid summary, the event table."""
        table = self._county_table()
        events_table = EventTable(self.config, self.sources, self.filters, self.impl, self._all_years(),
                                  tuple(self.spec.get("filters_disabled") or ()))
        events = events_table.build(None, self.counties)
        events["night"] = pd.DatetimeIndex(events["night"]).as_unit("ns")
        removed = self._removed_launch_nights(table)

        summary = self._type_summary(self._weights())
        shares = summary.summarize().drop(columns=["type_cells", "dominant_type"])
        classes = self._select_classes(shares)
        self.class_list = classes
        self.class_means = {k: float(shares[term(k)].mean()) for k in classes}
        table = table.join(shares)
        # Diagnostic columns: Paleozoic rock other than carbonate; carbonate outside the Paleozoic.
        carb = [term(f"{e}_carbonate") for e in ERA_NAMES]
        table["share_paleozoic_noncarbonate"] = table[term("paleozoic")] - table[term("paleozoic_carbonate")]
        table["share_carbonate"] = table[carb].sum(axis=1)
        table["share_carbonate_nonpaleozoic"] = table["share_carbonate"] - table[term("paleozoic_carbonate")]
        return table, events, removed, summary, events_table

    def analyse(self) -> tuple[EventTable, list[TestOutcome]]:
        table, events, removed, summary, events_table = self.prepare()
        classes = self.class_list
        years = self._split_years()
        outcomes = {k: TestOutcome(k) for k in classes}
        observed, self.pooled = {}, {}
        for tier in self.TIERS:
            counts, _, nights = self._period_counts(events, removed, years, table.index, tier)
            for k in classes:
                fit = self._fit(table, counts, nights, (term(k),))
                row = fit.coefficients.loc[[term(k)]].rename(index={term(k): "exposed"})
                outcomes[k].by_tier[tier] = TestResult(row, fit.n, int(counts.sum()), float("nan"))
                if tier == self.PRIMARY:
                    observed[k] = float(np.log(fit.coefficients.loc[term(k), "rate_ratio"]))
                    self.pooled[k] = fit.coefficients.loc[term(k)].to_dict()
            if tier == self.PRIMARY:
                counts_p, nights_p = counts, nights

        self.periods = {}
        for label, yrs in PERIODS.items():
            c, _, n = self._period_counts(events, removed, yrs, table.index, self.PRIMARY)
            self.periods[label] = {k: self._fit(table, c, n, (term(k),)).coefficients.loc[term(k)].to_dict() for k in classes}

        self.joint = {}
        for name, terms in self.p["joint_models"].items():
            coef = self._fit(table, counts_p, nights_p, tuple(terms)).coefficients
            self.joint[name] = {t: coef.loc[t].to_dict() for t in terms}

        checks = self.shift_checks = self._shift_classes(summary, table, counts_p, nights_p, observed, classes)
        for k in classes:
            outcomes[k].checks = {"shift_test": checks[k]}
        return events_table, [outcomes[k] for k in classes]

    def _shift_classes(self, summary, table, counts, nights, observed, classes) -> dict[str, dict]:
        rng = np.random.default_rng(self.p["seed"])
        c = self.counties.union_all().centroid
        null = {k: [] for k in classes}
        for trial in range(self.p["shift_trials"]):
            angle = rng.uniform(-self.p["max_rotate_deg"], self.p["max_rotate_deg"])
            dx, dy = rng.uniform(-self.p["max_shift_km"] * M_PER_KM, self.p["max_shift_km"] * M_PER_KM, size=2)
            moved = summary.summarize(summary.grid.shifted(angle, dx, dy, (c.x, c.y))).reindex(table.index)
            for k in classes:
                try:
                    fit = self._fit(table.assign(**{term(k): moved[term(k)]}), counts, nights, (term(k),))
                    null[k].append(float(np.log(fit.coefficients.loc[term(k), "rate_ratio"])))
                except Exception as exc:
                    log.warning("Shift trial %d, %s failed: %s", trial, k, exc)
            if (trial + 1) % 25 == 0:
                log.info("Shift test: %d/%d", trial + 1, self.p["shift_trials"])
        self.shift_null = {k: np.asarray(v) for k, v in null.items()}
        return {k: {"rate_ratio": float(np.exp(observed[k])), "p_value": two_sided_shift_p(observed[k], self.shift_null[k]),
                    "n_events": int(len(self.shift_null[k])),
                    "holds": bool(two_sided_shift_p(observed[k], self.shift_null[k]) < 0.05)} for k in classes}

    def _verdicts(self, outcomes: list[TestOutcome]) -> None:
        adjusted = benjamini_hochberg(pd.Series([o.by_tier[self.PRIMARY].p_value() for o in outcomes])).to_numpy()
        for o, q in zip(outcomes, adjusted):
            o.p_bh = float(q)
            o.verdict = "post hoc (no verdict)"

    # ------------------------------------------------------------------------------ report
    def extra_report_lines(self) -> list[str]:
        if not getattr(self, "class_list", None):
            return []
        f = lambda r: f"{r['rate_ratio']:.3f} ({r['ci_low']:.3f}–{r['ci_high']:.3f})"  # noqa: E731
        lines = ["## Post-hoc status", "",
                 "Every year of data was seen before this analysis (H-rockage-01 and H-rocktype-01). Estimates and "
                 "shift tests here describe the data; they confirm nothing. Power is not computed.", "",
                 "## Classes and estimates by period (filtered tier, per SD)", "",
                 "| Class | Mean county share | Pooled 2001–2023 | " + " | ".join(PERIODS) + " | Shift p (pooled) |",
                 "| --- | --- | --- | " + " | ".join("---" for _ in PERIODS) + " | --- |"]
        for k in self.class_list:
            row = [k.replace("_", " "), f"{self.class_means[k]:.1%}", f(self.pooled[k])]
            shift = self.shift_checks[k]["p_value"]
            row += [f(self.periods[p][k]) for p in PERIODS]
            row.append(f"{shift:.3f}")
            lines.append("| " + " | ".join(row) + " |")
        lines += ["", "## Era against rock type (joint models, pooled 2001–2023, filtered tier, per SD)", "",
                  "| Model | Term | Rate ratio (95% CI) | p |", "| --- | --- | --- | --- |"]
        for name, terms in self.joint.items():
            for t, r in terms.items():
                lines.append(f"| {name} | {t.replace('share_', '')} | {f(r)} | {r['p_value']:.3g} |")
        lines += ["", f"Crosses kept when their mean county share is at least {self.p['min_cross_share']:.0%} "
                  "(decided from the map alone)."]
        return lines

