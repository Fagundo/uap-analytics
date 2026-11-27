"""H-hatchpal-01: does the Paleozoic association found in NUFORC (H-rockera-01, post hoc) hold in an
independent, older catalog, Larry Hatch's *U* database, 1950-1999?

Same exposure (the county's share of surface rock whose midpoint age is Paleozoic, per SD), same model
(negative binomial rate model with state fixed effects, state-clustered errors, the H-persist-01 controls) and
same layer-shift test as the NUFORC analysis. What differs is the data: Hatch records from uap-data's export
(public tier: facts only), counted per county, with the offset taken from the county's mean population over
the 1950-1990 censuses instead of today's. No holiday or launch nights are removed: Hatch dates are often
approximate and few records have a time.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from statistics import NormalDist

import geopandas as gpd
import numpy as np
import pandas as pd

from uap_analytics.common.geo import CONUS_STATES, COUNTY_ID, WGS84
from uap_analytics.features.rock_age import ERA_NAMES
from uap_analytics.hypotheses.base import TestOutcome
from uap_analytics.hypotheses.designs.conditional_poisson import TestResult
from uap_analytics.hypotheses.rock_era import RockEraStudy
from uap_analytics.hypotheses.rock_type import term

log = logging.getLogger(__name__)
CLASS = "paleozoic"
TERM = term(CLASS)


@dataclass
class CatalogTable:
    """What the report card and regression fingerprint read from a study's data table."""
    records: pd.DataFrame
    summary: dict = field(default_factory=dict)
    rule_counts: dict = field(default_factory=dict)


def select_records(rows: pd.DataFrame, years: tuple[int, int], high_strangeness: float) -> tuple[pd.DataFrame, dict]:
    """Hatch rows to count: in the U.S. (contiguous states), dated within the years, with coordinates, not
    flagged as a hoax (HOX), and one row per cross-source duplicate group (lowest id kept). Adds the tier
    columns: in_all, in_filtered (not explained at high confidence by PURSUE's flags), in_high_strangeness."""
    n = {"hatch rows": len(rows)}
    r = rows.loc[rows["country"] == "USA"]
    n["in the U.S."] = len(r)
    r = r.loc[r["state"].isin(CONUS_STATES)]
    n["in the contiguous states"] = len(r)
    r = r.loc[r["date"].dt.year.between(*years)]
    n[f"dated {years[0]}-{years[1]}"] = len(r)
    r = r.loc[r["lat"].notna() & r["lon"].notna()]
    n["with coordinates"] = len(r)
    r = r.loc[~r["flags"].map(lambda f: "HOX" in f)]
    n["not flagged as a hoax"] = len(r)
    r = r.sort_values("sighting_id")
    grouped = r["dedup_group"].notna()
    r = pd.concat([r.loc[~grouped], r.loc[grouped].drop_duplicates("dedup_group")]).sort_values("sighting_id")
    n["one per duplicate group"] = len(r)
    r = r.assign(year=r["date"].dt.year, in_all=True, in_filtered=r["explanation_tier"] != "explained",
                 in_high_strangeness=r["strangeness"] >= high_strangeness)
    return r.reset_index(drop=True), n


def assign_counties(records: pd.DataFrame, counties: gpd.GeoDataFrame) -> pd.Series:
    """County id for each record's point (missing when the point is in no county: water, a border)."""
    pts = gpd.GeoDataFrame(records[["sighting_id"]], geometry=gpd.points_from_xy(records["lon"], records["lat"]),
                           crs=WGS84).to_crs(counties.crs)
    joined = gpd.sjoin(pts, counties[[COUNTY_ID, "geometry"]], how="left", predicate="within")
    return joined[~joined.index.duplicated()][COUNTY_ID].reindex(records.index)


class HatchPaleozoicStudy(RockEraStudy):
    HYPOTHESIS_ID = "H-hatchpal-01"
    PARAM_KEY = "hatch_paleozoic"
    MODEL_NAME = "hatch_paleozoic"
    TIERS = ("all", "filtered", "high_strangeness")
    PRIMARY = "filtered"
    TEST_LABELS = {CLASS: "Paleozoic share of surface rock (per SD)"}
    CHECK_LABELS = {"shift_test": "Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05)"}

    # ------------------------------------------------------------------------------ inputs
    def _records(self, table: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        rows = self.sources.export_tables().catalog("hatch")
        records, counts = select_records(rows, self._all_years(), float(self.p["high_strangeness_min"]))
        records[COUNTY_ID] = assign_counties(records, self.counties)
        located = records[COUNTY_ID].notna() & records[COUNTY_ID].isin(table.index)
        counts["in a county with a population history"] = int(located.sum())
        return records.loc[located].reset_index(drop=True), counts

    def _historical_table(self) -> pd.DataFrame:
        table = self._county_table()
        hist = self.sources.historical_population(tuple(self.p["population_censuses"])).load().set_index(COUNTY_ID)
        table["population_today"] = table["population"]
        table["population"] = hist["population_hist"].reindex(table.index)
        self.population_coverage = {"counties": len(table),
                                    "counties without a population history": int(table["population"].isna().sum())}
        return table.loc[table["population"].notna() & (table["population"] > 0)]

    def _tier_counts(self, records: pd.DataFrame, years: tuple[int, int], tier: str, index: pd.Index):
        """(counts per county, county-nights): nights are the days in the years, the same for every county."""
        kept = records.loc[records["year"].between(*years) & records[f"in_{tier}"]]
        counts = kept.groupby(COUNTY_ID).size().reindex(index, fill_value=0)
        days = float(len(pd.date_range(f"{years[0]}-01-01", f"{years[1]}-12-31", freq="D")))
        return counts, pd.Series(days, index=index)

    # ------------------------------------------------------------------------------ analysis
    def prepare(self):
        table = self._historical_table()
        records, counts = self._records(table)
        summary = self._type_summary(self._weights())
        shares = summary.summarize()
        table = table.join(shares[[term(e) for e in ERA_NAMES] + [term("paleozoic_carbonate")]])
        table["share_paleozoic_noncarbonate"] = table[TERM] - table[term("paleozoic_carbonate")]
        self.selection = counts
        self.class_means = {CLASS: float(table[TERM].mean())}
        return table, records, summary

    def analyse(self):
        table, records, summary = self.prepare()
        years = self._split_years()
        o = TestOutcome(CLASS)
        for tier in self.TIERS:
            counts, nights = self._tier_counts(records, years, tier, table.index)
            fit = self._fit(table, counts, nights, (TERM,))
            row = fit.coefficients.loc[[TERM]].rename(index={TERM: "exposed"})
            o.by_tier[tier] = TestResult(row, fit.n, int(counts.sum()), float("nan"))
            if tier == self.PRIMARY:
                primary = (counts, nights, float(np.log(fit.coefficients.loc[TERM, "rate_ratio"])))
        counts, nights, observed = primary
        o.checks = {"shift_test": self._shift_classes(summary, table, counts, nights, {CLASS: observed}, [CLASS])[CLASS]}
        o.power = self._power(table, records)
        self.secondary = {name: {t: c.loc[t].to_dict() for t in terms}
                          for name, terms in self.p["joint_models"].items()
                          for c in [self._fit(table, counts, nights, tuple(terms)).coefficients]}
        self.decades = {}
        for start in range(years[0] - years[0] % 10, years[1] + 1, 10):
            span = (max(start, years[0]), min(start + 9, years[1]))
            c, n = self._tier_counts(records, span, self.PRIMARY, table.index)
            self.decades[f"{span[0]}-{span[1]}"] = {"records": int(c.sum()),
                                                     **self._fit(table, c, n, (TERM,)).coefficients.loc[TERM].to_dict()}
        in_years = records["year"].between(*years)
        data = CatalogTable(records.loc[in_years, ["sighting_id", "year", COUNTY_ID]], summary={
            "reports": int(in_years.sum()), "events": int(in_years.sum()),
            "events_in_counties": int(in_years.sum()), "selection": self.selection},
            rule_counts={"explained by PURSUE's flags (left out of the filtered tier)":
                         int((in_years & ~records["in_filtered"]).sum()), "possible_only": 0})
        return data, [o]

    def _power(self, table: pd.DataFrame, records: pd.DataFrame) -> float:
        """Two-sided power for rate ratio 1.10 or 1/1.10 from the explore-period standard error (not scaled:
        county-level variation, not record counts, sets it)."""
        start, end = (int(y) for y in self.spec["splits"]["explore"])
        counts, nights = self._tier_counts(records, (start, end), self.PRIMARY, table.index)
        c = self._fit(table, counts, nights, (TERM,)).coefficients.loc[TERM]
        se = (np.log(c["ci_high"]) - np.log(c["ci_low"])) / (2 * 1.959964)
        p = self.impl["parameters"]["power"]
        z = NormalDist().inv_cdf(1 - p["alpha"] / 2)
        self.power_inputs = {"se_explore": float(se), "records_explore": int(counts.sum())}
        return float(NormalDist().cdf(np.log(p["rate_ratio"]) / se - z) + NormalDist().cdf(-np.log(p["rate_ratio"]) / se - z))

    def _verdicts(self, outcomes: list[TestOutcome]) -> None:
        p = self.impl["parameters"]["power"]
        for o in outcomes:
            o.p_bh = o.by_tier[self.PRIMARY].p_value()          # one primary test: no correction
            if self.split == "explore":
                o.verdict = "exploration (no verdict)"
                continue
            main = o.by_tier[self.PRIMARY].terms.loc["exposed"]
            if o.p_bh < 0.05 and o.checks["shift_test"]["holds"]:
                o.verdict = ("confirmed: replicates (more reports)" if main["rate_ratio"] > 1
                             else "confirmed: opposite direction (fewer reports)")
            elif o.power < p["underpowered_below"]:
                o.verdict = "underpowered"
            elif o.power >= p["refute_requires"] and 1 / p["rate_ratio"] < main["ci_low"] and main["ci_high"] < p["rate_ratio"]:
                o.verdict = "refuted"
            else:
                o.verdict = "inconclusive"

    # ------------------------------------------------------------------------------ report
    def extra_report_lines(self) -> list[str]:
        if not getattr(self, "selection", None):
            return []
        f = lambda r: f"{r['rate_ratio']:.3f} ({r['ci_low']:.3f}–{r['ci_high']:.3f})"  # noqa: E731
        lines = ["## Hatch records", "", "| Step | Records |", "| --- | --- |"]
        lines += [f"| {k} | {v:,} |" for k, v in self.selection.items()]
        lines += ["", f"Mean county Paleozoic share: {self.class_means[CLASS]:.1%}. Offset: mean county population "
                  f"over the {', '.join(map(str, self.p['population_censuses']))} censuses; "
                  f"{self.population_coverage['counties without a population history']} of "
                  f"{self.population_coverage['counties']:,} counties have none and are left out.", "",
                  "## By decade (filtered tier, per SD; descriptive)", "", "| Years | Records | Rate ratio (95% CI) |",
                  "| --- | --- | --- |"]
        lines += [f"| {k} | {v['records']:,} | {f(v)} |" for k, v in self.decades.items()]
        lines += ["", "## Paleozoic carbonate and other Paleozoic rock (joint model, filtered tier; descriptive)", "",
                  "| Model | Term | Rate ratio (95% CI) | p |", "| --- | --- | --- | --- |"]
        for name, terms in self.secondary.items():
            for t, r in terms.items():
                lines.append(f"| {name} | {t.replace('share_', '')} | {f(r)} | {r['p_value']:.3g} |")
        null = getattr(self, "shift_null", {}).get(CLASS)
        if null is not None and len(null):
            q = np.exp(np.quantile(null, [0.025, 0.5, 0.975]))
            lines += ["", f"Shift-test copies fitted: {len(null)}; rate ratio 2.5% {q[0]:.3f}, median {q[1]:.3f}, "
                      f"97.5% {q[2]:.3f}."]
        if getattr(self, "power_inputs", None):
            lines += ["", f"Power: two-sided for rate ratio 1.10 or 1/1.10 at alpha 0.05, from the explore-period "
                      f"standard error ({self.power_inputs['se_explore']:.3f}, {self.power_inputs['records_explore']:,} records)."]
        lines += ["", "Hatch caveats: the catalog was compiled by one person from press, NICAP, Blue Book and other "
                  "files up to the early 2000s, so its coverage follows what was reported and collected, not what "
                  "was seen. The observer controls are today's (light pollution, roads, airports, census shares), "
                  "an approximation for 1950-1999; the offset is the period's population. Report-card notes about "
                  "matched nights and NUFORC rules do not apply to this study."]
        return lines
