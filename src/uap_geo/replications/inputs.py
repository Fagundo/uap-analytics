"""The replications' inputs, read from the combined export (the only module here that touches it).

Sightings keep each source's file order (``source_order``), because the original tests collapse to one report per
state and month by keeping the last in that order, and their shuffles are seeded on it.
"""
from __future__ import annotations

import json
from datetime import date

import pandas as pd

from uap_geo.replications.bluebook.index import IndexRow
from uap_geo.replications.common.dates import Precision, Span
from uap_geo.replications.common.places import StatePlacer
from uap_geo.replications.nuclear.sites import NuclearTest
from uap_geo.replications.programs.catalog import Program, Site
from uap_geo.replications.programs.sightings import Sighting

EXCLUDE_FLAGS = frozenset({"HOX"})                # suspected hoaxes, as the catalogs flag them


def _float(text: str) -> float | None:
    return float(text) if text not in ("", None) else None


def _span(row) -> Span:
    return Span(date.fromisoformat(row["date_start"]), date.fromisoformat(row["date_end"]),
                Precision.parse(row["date_precision"]))


class ReplicationInputs:
    def __init__(self, tables, placer: StatePlacer | None = None):
        self.tables = tables                      # ExportTables
        self.placer = placer or StatePlacer()

    # ------------------------------------------------------------------ layers
    def programs(self) -> list[Program]:
        rows = self.tables.layer("flight_programs")
        attrs = rows["attributes"].map(json.loads)
        out = []
        for i in rows.index[~rows["item_id"].str.contains(":site:")]:
            a, pid = attrs[i], attrs[i]["program"]
            site_rows = rows.loc[rows["item_id"].str.startswith(f"program:{pid}:site:")]
            order = site_rows["item_id"].str.rsplit(":", n=1).str[1].astype(int).sort_values()
            sites = tuple(Site(attrs[j]["site"], float(rows.at[j, "lat"]), float(rows.at[j, "lon"])) for j in order.index)
            out.append(Program(pid, rows.at[i, "label"], a["kind"], date.fromisoformat(rows.at[i, "start_utc"][:10]),
                               date.fromisoformat(rows.at[i, "end_utc"][:10]),
                               frozenset(s for s in a["states"].split(",") if s), sites))
        return out

    def nuclear_tests(self) -> list[NuclearTest]:
        rows = self.tables.layer("nuclear_tests")
        out = []
        for r in rows.itertuples(index=False):
            a = json.loads(r.attributes)
            if r.lat == "" or r.lon == "":
                continue
            out.append(NuclearTest(r.item_id.removeprefix("nuclear:"), date.fromisoformat(r.start_utc[:10]), a["country"],
                                   a["kind"], float(r.lat), float(r.lon), r.label))
        return out

    # ------------------------------------------------------------------ sightings
    def pursue_sightings(self) -> list[Sighting]:
        """Dated sighting incidents from the released files placed in one state from their location text (the
        original test's placement, not the export's geocoded state)."""
        out = []
        for r in self.tables.rows(("pursue",)).itertuples(index=False):
            links = json.loads(r.links or "{}")
            if links.get("event_type", "sighting") != "sighting":
                continue
            state = self.placer.from_text(r.place_text)
            if state:
                doc = (links.get("doc_ids") or "").split(",")[0]
                out.append(Sighting(f"incident:{links['incident_id']}", _span(r._asdict()), state, "pursue", doc))
        return out

    def external_sightings(self, source: str, require_flag: str | None = None, world: bool = False,
                           min_precision: Precision = Precision.MONTH) -> list[Sighting]:
        """An outside catalog's reports dated to the month or better, without suspected hoaxes.

        By default only U.S. reports placed in one state (the catalog's state, or coordinates placed by point in
        polygon). With ``world=True``, every report with coordinates; ``state`` then holds the state when known,
        otherwise the country."""
        out = []
        for r in self.tables.rows((source,)).itertuples(index=False):
            row = r._asdict()
            span = _span(row)
            if span.precision < min_precision:
                continue
            flags = set(json.loads(r.flags or "[]"))
            if require_flag and require_flag not in flags or flags & EXCLUDE_FLAGS:
                continue
            # only the catalog's own coordinates, as the original used (not places geocoded from the text)
            lat, lon = (_float(r.lat), _float(r.lon)) if r.coord_precision == "catalog" else (None, None)
            country = r.country or None
            state = self.placer.name(r.state)
            if state is None and lat is not None and country == "USA":
                state = self.placer.from_point(lat, lon)
            if world:
                if lat is None:
                    continue
                state = state or country or ""
            elif not state:
                continue
            out.append(Sighting(r.sighting_id, span, state, source, f"{state}:{span.start.year}", lat, lon))
        return out

    def bluebook_index(self) -> list[IndexRow]:
        out = []
        for r in self.tables.rows(("bluebook-index",)).itertuples(index=False):
            flags = json.loads(r.flags or "[]")
            category = next((f.removeprefix("BB:") for f in flags if f.startswith("BB:")), None)
            family = next((f.removeprefix("BBF:") for f in flags if f.startswith("BBF:")), None)
            if category is None:
                continue
            start = date.fromisoformat(r.date_start)
            out.append(IndexRow(start.year, start.month, self.placer.name(r.state), r.country or None, category, family))
        return out


def frame_of(sightings: list[Sighting]) -> pd.DataFrame:
    """A small table of sightings (for checks and counts)."""
    return pd.DataFrame([{"id": s.id, "date": s.date.start, "state": s.state, "source": s.source,
                          "lat": s.lat, "lon": s.lon} for s in sightings])
