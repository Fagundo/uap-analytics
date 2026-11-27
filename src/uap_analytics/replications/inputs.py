"""The replications' inputs, read from the combined export (the only module here that touches it).

Sightings keep each source's file order (``source_order``), because the original tests collapse to one report per
state and month by keeping the last in that order, and their shuffles are seeded on it.
"""
from __future__ import annotations

import json
from datetime import date

import pandas as pd

from uap_analytics.replications.bluebook.index import IndexRow
from uap_analytics.replications.networks.corpus import DocumentInfo, EntityCorpus, MentionRow, NodeInfo, PageText
from uap_analytics.replications.common.dates import Precision, Span
from uap_analytics.replications.common.places import StatePlacer
from uap_analytics.replications.nuclear.sites import NuclearTest
from uap_analytics.replications.programs.catalog import Program, Site
from uap_analytics.replications.programs.sightings import Sighting

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
        self.entities = EntityInputs(tables)

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


class EntityInputs:
    """The released documents' entity graph, page text, incidents and the project's datasets, from the export."""

    def __init__(self, tables):
        self.tables = tables

    def documents(self) -> list[DocumentInfo]:
        return [DocumentInfo(r.doc_id, r.agency, r.doc_date or None, r.release)
                for r in self.tables.entity("documents").itertuples(index=False)]

    def corpus(self) -> EntityCorpus:
        """People and organizations as nodes (people lifted to the organization their affiliation names), and who
        appears on which page, from the mentions in id order."""
        nodes = [NodeInfo(f"org:{r.org_id}", "org", int(r.org_id), r.canonical_name)
                 for r in self.tables.entity("organizations").itertuples(index=False)]
        nodes += [NodeInfo(f"person:{r.person_id}", "person", int(r.person_id), r.canonical_name,
                           r.is_placeholder in ("1", "True", "true"),
                           f"org:{r.affiliation_org_id}" if r.affiliation_org_id else None)
                  for r in self.tables.entity("people").itertuples(index=False)]
        mentions = [MentionRow(r.doc_id, int(r.page), r.entity_type.lower(), int(r.entity_id) if r.entity_id else None,
                               r.role or None, r.raw_text)
                    for r in self.tables.entity("mentions").itertuples(index=False)]
        return EntityCorpus.build(self.documents(), nodes, mentions)

    def pages(self) -> list[PageText]:
        return [PageText(r.doc_id, int(r.page), r.text) for r in self.tables.entity("page_text").itertuples(index=False)]

    def incidents(self) -> list:
        """Incidents with the fields the claims report reads (lists decoded from their JSON text)."""
        from types import SimpleNamespace
        out = []
        for r in self.tables.entity("incidents").itertuples(index=False):
            out.append(SimpleNamespace(incident_id=int(r.incident_id), date=r.date or None,
                                       location_text=r.location_text or None, summary=r.summary or None,
                                       doc_ids=json.loads(r.doc_ids or "[]"), status=r.status or None,
                                       verdicts=json.loads(r.verdicts or "[]")))
        return out

    def dataset(self, name: str) -> dict:
        return self.tables.dataset(name)


def frame_of(sightings: list[Sighting]) -> pd.DataFrame:
    """A small table of sightings (for checks and counts)."""
    return pd.DataFrame([{"id": s.id, "date": s.date.start, "state": s.state, "source": s.source,
                          "lat": s.lat, "lon": s.lon} for s in sightings])
