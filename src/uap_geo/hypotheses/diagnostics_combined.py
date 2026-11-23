"""Post hoc: the geology associations on every catalog in uap-data's export, 1950-2023, with time fixed effects.

Exploratory and labelled post hoc: it uses the Hatch 1960-1999 records, so H-hatchpal-01 can no longer be a
confirmation. Quick models only (no shift test).

Data: one row per county x decade (1950s ... 2020s, the last 2020-2023). Records: every source in the export
(NUFORC, Hatch, NICAP, Blue Book unknowns and index, PURSUE's incidents, Magonia), contiguous U.S., placed at
site or town level, not a hoax, not a NUFORC repeat, not explained at high confidence by uap-data's flags; one
per cross-source duplicate group in the combined set. Offset: the county's population at the decade's census
(1950-1990 from the Census 1900-1990 counts, 2000 and 2010 from the Census API, the 2020s from today's
estimates) x days in the decade. Controls: the H-persist-01 set (today's values). Standard errors clustered by
state (counties repeat across decades).

Time is handled three ways, side by side:
  cross-section   records summed over 1950-2023 per county, state fixed effects (as the registered studies)
  state + decade  panel with state and decade fixed effects (decade-wide swings in reporting removed)
  state x decade  panel with one effect per state per decade (each county compared with its own state's
                  counties in the same decade; regional reporting shifts over time removed too)
County fixed effects cannot be used: geology does not change over time, so they would absorb it.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from uap_geo.common.geo import CONUS_STATES, COUNTY_ID
from uap_geo.features.rock_age import ERA_NAMES
from uap_geo.hypotheses.hatch_paleozoic import assign_counties
from uap_geo.hypotheses.rock_type import term
from uap_geo.training.models import ModelSpec, NegBinRateModel

DECADES = list(range(1950, 2030, 10))
LAST_YEAR = 2023
EXPOSURES = {"share_paleozoic": "Paleozoic share", "share_carbonate": "Carbonate share (all eras)"}
SOURCES = ["combined", "nuforc", "hatch", "nicap", "bluebook-index", "bluebook-unknowns", "pursue", "magonia"]


def select(rows: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    n = {"rows in the export": len(rows)}
    us = rows["country"].isna() | (rows["country"] == "USA")
    r = rows.loc[us & rows["state"].isin(CONUS_STATES)]
    n["contiguous states"] = len(r)
    r = r.loc[r["coord_precision"].isin(["site", "town"]) & r["lat"].notna()]
    n["placed at site or town level"] = len(r)
    r = r.loc[r["date"].dt.year.between(DECADES[0], LAST_YEAR)]
    n[f"dated {DECADES[0]}-{LAST_YEAR}"] = len(r)
    r = r.loc[~r["flags"].map(lambda f: "HOX" in f or "DUPLICATE" in f)]
    n["not a hoax or NUFORC repeat"] = len(r)
    r = r.loc[r["explanation_tier"] != "explained"]
    n["not explained (filtered)"] = len(r)
    return r.reset_index(drop=True), n


def one_per_group(r: pd.DataFrame) -> pd.DataFrame:
    r = r.sort_values("sighting_id")
    grouped = r["dedup_group"].notna()
    return pd.concat([r.loc[~grouped], r.loc[grouped].drop_duplicates("dedup_group")])


class CombinedPanelDiagnostics:
    def __init__(self, study) -> None:
        self.study = study

    def _population(self, table: pd.DataFrame) -> pd.DataFrame:
        st = self.study
        hist = st.sources.historical_population(tuple(range(1950, 2000, 10))).by_census()
        pop = pd.DataFrame(index=table.index)
        for d in DECADES:
            if d <= 1990:
                pop[d] = hist[d].reindex(table.index) if d in hist.columns else np.nan
            elif d in (2000, 2010):
                pop[d] = st.sources.census_population(d).load().reindex(table.index)
            else:
                pop[d] = table["population_today"]
        return pop

    def _panel(self, table: pd.DataFrame, pop: pd.DataFrame, records: pd.DataFrame) -> pd.DataFrame:
        rec = records.assign(decade=(records["date"].dt.year // 10) * 10)
        counts = rec.groupby([COUNTY_ID, "decade"]).size()
        rows = []
        for d in DECADES:
            days = len(pd.date_range(f"{d}-01-01", f"{min(d + 9, LAST_YEAR)}-12-31", freq="D"))
            part = table.copy()
            part["decade"] = d
            part["report_count"] = counts.xs(d, level="decade").reindex(table.index, fill_value=0) \
                if d in counts.index.get_level_values("decade") else 0
            part["population"] = pop[d] * days / (10 * 365.25)
            rows.append(part)
        panel = pd.concat(rows)
        panel["state_decade"] = panel["state_fips"].astype(str) + "_" + panel["decade"].astype(str)
        panel.index = pd.Index(panel.index.astype(str) + "_" + panel["decade"].astype(str), name="county_decade")
        return panel

    def _fit(self, data: pd.DataFrame, exposure: str, fixed: tuple[str, ...]):
        st = self.study
        spec = ModelSpec("combined_panel", (*st.controls, exposure), fixed)
        return NegBinRateModel(spec, quiet=True, cluster="state_fips").fit(data).coefficients.loc[exposure]

    def inputs(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
        """(county table with Paleozoic and carbonate shares, population by decade, selected records placed in a
        county, selection counts), shared by the combined and stacked diagnostics."""
        st = self.study
        table, _, _ = st.prepare()             # county table: controls, historical population, era shares
        shares = st._type_summary(st._weights()).summarize()
        table["share_carbonate"] = shares[[term(f"{e}_carbonate") for e in ERA_NAMES]].sum(axis=1).reindex(table.index)
        pop = self._population(table)
        table = table.loc[pop.notna().all(axis=1) & (pop > 0).all(axis=1)]
        pop = pop.loc[table.index]
        rows, steps = select(st.sources.export_tables().all_sightings())
        rows[COUNTY_ID] = assign_counties(rows, st.counties)
        rows = rows.loc[rows[COUNTY_ID].isin(table.index)]
        steps["in a county with populations for every decade"] = len(rows)
        return table, pop, rows, steps

    def run(self) -> Path:
        st = self.study
        table, pop, rows, steps = self.inputs()

        f = lambda r: f"{r['rate_ratio']:.3f} ({r['ci_low']:.3f}–{r['ci_high']:.3f})"  # noqa: E731
        stars = lambda p: "**" if p < 0.01 else ("*" if p < 0.05 else "")  # noqa: E731
        lines = ["# Post hoc: geology on every catalog, 1950–2023, with time fixed effects", "",
                 __doc__.split("\n\n", 1)[1].strip(), "",
                 "## Records", "", "| Step | Records |", "| --- | --- |"]
        lines += [f"| {k} | {v:,} |" for k, v in steps.items()]
        combined = one_per_group(rows)
        lines.append(f"| combined: one per cross-source duplicate group | {len(combined):,} |")
        by_source = rows.groupby("source").size()
        lines += ["", "By source (before combining): " + ", ".join(f"{s} {by_source.get(s, 0):,}" for s in SOURCES[1:]) + ".",
                  "", "## Rate ratio per SD (95% CI); * p < 0.05, ** p < 0.01", ""]
        for exposure, label in EXPOSURES.items():
            lines += [f"### {label}", "", "| Data | Records | Cross-section, state FE | Panel, state + decade FE | "
                      "Panel, state x decade FE |", "| --- | --- | --- | --- | --- |"]
            for src in SOURCES:
                recs = combined if src == "combined" else rows.loc[rows["source"] == src]
                if len(recs) < 300:
                    lines.append(f"| {src} | {len(recs):,} | (too few records) | | |")
                    continue
                panel = self._panel(table, pop, recs)
                cells = []
                cross = panel.groupby(panel.index.str[:5]).agg({"report_count": "sum", "population": "sum"})
                cross = table.drop(columns=["population"]).join(cross)
                for data, fixed in ((cross, ("state_fips",)), (panel, ("state_fips", "decade")), (panel, ("state_decade",))):
                    try:
                        r = self._fit(data, exposure, fixed)
                        cells.append(f"{f(r)}{stars(r['p_value'])}")
                    except Exception as exc:
                        cells.append(f"failed ({type(exc).__name__})")
                lines.append(f"| {src} | {len(recs):,} | " + " | ".join(cells) + " |")
            lines.append("")

        lines += ["## Combined data by decade (cross-section within the decade, state FE)", "",
                  "| Decade | Records | Paleozoic share | Carbonate share |", "| --- | --- | --- | --- |"]
        panel = self._panel(table, pop, combined)
        for d in DECADES:
            part = panel.loc[panel["decade"] == d]
            cells = []
            for exposure in EXPOSURES:
                try:
                    r = self._fit(part, exposure, ("state_fips",))
                    cells.append(f"{f(r)}{stars(r['p_value'])}")
                except Exception as exc:
                    cells.append(f"failed ({type(exc).__name__})")
            lines.append(f"| {d}s | {int(part['report_count'].sum()):,} | " + " | ".join(cells) + " |")
        lines += ["", "Descriptive and post hoc. Counts describe reporting and collection, not phenomena; the catalogs "
                  "overlap (Hatch drew on NICAP and Blue Book), so the per-source rows are not independent."]
        out = st.root / "results" / "H-hatchpal-01" / "diagnostics"
        out.mkdir(parents=True, exist_ok=True)
        path = out / "combined_time_fe.md"
        path.write_text("\n".join(lines) + "\n")
        return path
