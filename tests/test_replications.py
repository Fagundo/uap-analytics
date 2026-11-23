"""Replications of the data repository's population tests: inputs from the export, the tests, parity."""
import json
from datetime import date

import pandas as pd
import pytest

from uap_geo.replications.common.dates import Precision, Span
from uap_geo.replications.common.places import StatePlacer
from uap_geo.replications.inputs import ReplicationInputs
from uap_geo.replications.parity import compare
from uap_geo.replications.programs.catalog import Program, Site
from uap_geo.replications.programs.shuffle import CoincidenceTest, ProximityTest
from uap_geo.replications.programs.sightings import Sighting, one_per

COLS = ["sighting_id", "source", "date_start", "date_end", "date_precision", "lat", "lon", "coord_precision",
        "country", "state", "place_text", "flags", "links", "source_order"]


def _row(sid, source, start, prec="day", lat="", lon="", cp="none", country="USA", state="", place="", flags=(),
         links=None, order=""):
    return dict(zip(COLS, [sid, source, start, start, prec, lat, lon, cp, country, state, place, json.dumps(list(flags)),
                           json.dumps(links or {}), str(order)]))


class FakeTables:
    def __init__(self, rows, layers):
        self.frame, self.layers = pd.DataFrame(rows, columns=COLS), layers

    def rows(self, sources):
        r = self.frame.loc[self.frame["source"].isin(sources)].copy()
        r["_o"] = pd.to_numeric(r["source_order"].replace("", pd.NA))
        return r.sort_values(["source", "_o"], kind="stable").drop(columns="_o").reset_index(drop=True)

    def layer(self, name):
        return self.layers[name]


def _layers():
    attrs = {"program": "u2", "kind": "aircraft", "states": "Nevada"}
    programs = pd.DataFrame([
        {"item_id": "program:u2", "start_utc": "1955-08-01", "end_utc": "1975-12-31", "lat": "", "lon": "",
         "label": "U-2", "attributes": json.dumps(attrs)},
        {"item_id": "program:u2:site:1", "start_utc": "1955-08-01", "end_utc": "1975-12-31", "lat": "37.8", "lon": "-116.8",
         "label": "U-2: B", "attributes": json.dumps({**attrs, "site": "B"})},
        {"item_id": "program:u2:site:0", "start_utc": "1955-08-01", "end_utc": "1975-12-31", "lat": "37.235", "lon": "-115.81",
         "label": "U-2: Groom", "attributes": json.dumps({**attrs, "site": "Groom Lake"})}])
    nuclear = pd.DataFrame([{"item_id": "nuclear:N1", "start_utc": "1957-07-05", "lat": "37.1", "lon": "-116.0",
                             "label": "Priscilla", "attributes": json.dumps({"country": "USA", "kind": "air"})}])
    return {"flight_programs": programs, "nuclear_tests": nuclear}


@pytest.fixture(scope="module")
def placer():
    return StatePlacer()


def test_placer_names_text_and_points(placer):
    assert placer.name("NM") == "New Mexico" and placer.name("DC") == "District of Columbia"
    assert placer.from_text("Holloman AFB, N.M.") == "New Mexico"
    assert placer.from_text("Washington, D.C.") == "District of Columbia"
    assert placer.from_text("Texas and Oklahoma") is None                    # two states: not placed
    assert placer.from_point(35.08, -106.65) == "New Mexico"
    lat, lon = placer.centroid("Kansas")
    assert 37 < lat < 40 and -100 < lon < -96


def test_inputs_from_export(placer):
    rows = [
        _row("hatch:2", "hatch", "1957-06-01", lat="37.2", lon="-115.8", cp="catalog", state="NV", order=1),
        _row("hatch:1", "hatch", "1957-06-01", prec="month", state="NM", flags=["BBK"], order=0),
        _row("hatch:3", "hatch", "1957-06-01", prec="year", state="NM", order=2),             # year only: dropped
        _row("hatch:4", "hatch", "1957-06-01", state="NM", flags=["HOX"], order=3),           # hoax: dropped
        _row("hatch:5", "hatch", "1957-06-01", lat="35.1", lon="-106.6", cp="town", state="", order=4),  # geocoded: no coords, no state
        _row("hatch:6", "hatch", "1960-01-01", lat="48.8", lon="2.3", cp="catalog", country="France", order=5),
        _row("pursue:a", "pursue", "1949-01-30", place="Los Alamos", links={"incident_id": "4", "doc_ids": "D017,D018",
                                                                              "event_type": "sighting"}, order=1),
        _row("pursue:b", "pursue", "1947-07-08", place="Roswell, New Mexico", links={"incident_id": "9", "event_type": "recovery"}, order=0),
        _row("bluebook-index:1", "bluebook-index", "1956-03-01", prec="month", state="AZ", flags=["BB:other", "BBF:weather or optical"]),
    ]
    inp = ReplicationInputs(FakeTables(rows, _layers()), placer)
    hatch = inp.external_sightings("hatch")
    assert [s.id for s in hatch] == ["hatch:1", "hatch:2"]                     # file order; filters applied
    assert hatch[1].state == "Nevada" and hatch[1].lat == 37.2 and hatch[0].lat is None
    assert [s.id for s in inp.external_sightings("hatch", require_flag="BBK")] == ["hatch:1"]
    world = inp.external_sightings("hatch", world=True)
    assert [(s.id, s.state) for s in world] == [("hatch:2", "Nevada"), ("hatch:6", "France")]
    pursue = inp.pursue_sightings()
    assert [(s.id, s.state, s.group) for s in pursue] == [("incident:4", "New Mexico", "D017")]   # recovery left out
    (prog,) = inp.programs()
    assert prog.states == frozenset({"Nevada"}) and [s.name for s in prog.sites] == ["Groom Lake", "B"]
    assert prog.start == date(1955, 8, 1) and prog.end == date(1975, 12, 31)
    (bb,) = inp.bluebook_index()
    assert (bb.year, bb.month, bb.state, bb.category, bb.family) == (1956, 3, "Arizona", "other", "weather or optical")
    (nt,) = inp.nuclear_tests()
    assert nt.id == "N1" and nt.kind == "air" and nt.day == date(1957, 7, 5)


def test_shuffle_tests_and_collapse():
    prog = Program("p", "P", "aircraft", date(1955, 1, 1), date(1955, 12, 31), frozenset({"Nevada"}), (Site("G", 37.2, -115.8),))
    day = lambda y: Span(date(y, 6, 1), date(y, 6, 1), Precision.DAY)
    ss = [Sighting("a", day(1955), "Nevada", "x", lat=37.3, lon=-115.9), Sighting("b", day(1960), "Ohio", "x"),
          Sighting("c", day(1955), "Ohio", "x"), Sighting("d", day(1960), "Nevada", "x", lat=37.2, lon=-115.8)]
    r = CoincidenceTest([prog], shuffles=50).run("t", ss)
    assert (r.sightings, r.observed, [m["id"] for m in r.matches]) == (4, 1, ["a"])
    d = ProximityTest([prog], radius_km=50, shuffles=50).run("t", ss)
    assert (d.sightings, d.observed) == (2, 1)
    assert [s.id for s in one_per(ss, lambda s: s.state)] == ["d", "c"]        # last per key, first-seen key order


def test_parity_finds_differences():
    out = {"tests": [{"dataset": "hatch", "method": "state", "radius_km": None, "sightings": 10, "observed": 3,
                      "null_mean": 2.5, "ratio": 1.2, "p_value": 0.3, "per_program": {"u2": {"name": "U-2", "observed": 3,
                      "null_mean": 2.5, "p_value": 0.3}}, "matches": [{"id": "hatch:1"}, {"id": "hatch:2"}, {"id": "hatch:3"}]}],
           "local_share_by_year": {}}
    from uap_geo.replications.parity import reduce
    ref = reduce("programs", out)
    assert compare("programs", ref, out).ok
    out["tests"][0]["observed"] = 4
    out["tests"][0]["matches"].pop()
    diffs = compare("programs", ref, out).differences
    assert any("observed" in d for d in diffs) and any("matches_sha256" in d for d in diffs)


def test_network_corpus_routing_and_claims_from_export():
    from uap_geo.replications.inputs import EntityInputs
    from uap_geo.replications.networks.routing import RoutingAnalyzer

    ent = {
        "documents": pd.DataFrame([{"doc_id": "D1", "agency": "FBI", "doc_date": "1952-07-29", "release": "r1"}]),
        "organizations": pd.DataFrame([{"org_id": "4", "canonical_name": "FBI"}, {"org_id": "5", "canonical_name": "USAF"}]),
        "people": pd.DataFrame([
            {"person_id": "1", "canonical_name": "J. Edgar Hoover", "is_placeholder": "0", "affiliation_org_id": "4"},
            {"person_id": "2", "canonical_name": "D. M. Ladd", "is_placeholder": "0", "affiliation_org_id": "5"}]),
        "mentions": pd.DataFrame([
            {"doc_id": "D1", "page": "1", "entity_type": "person", "entity_id": "2", "role": "addressee", "raw_text": "Mr.  Ladd"},
            {"doc_id": "D1", "page": "2", "entity_type": "person", "entity_id": "1", "role": "author", "raw_text": "Hoover"},
            {"doc_id": "D1", "page": "2", "entity_type": "location", "entity_id": "9", "role": "", "raw_text": "DC"}]),
        "incidents": pd.DataFrame([{"incident_id": "3", "date": "1952-07-19", "location_text": "Washington, D.C.",
                                    "summary": "radar", "doc_ids": '["D1"]', "status": "unresolved", "verdicts": "[]"}]),
    }

    class T:
        def entity(self, name):
            return ent[name]

    e = EntityInputs(T())
    corpus = e.corpus()
    assert corpus.nodes["person:1"].affiliation_org == "org:4" and corpus.quotes[(("D1", 1), "person:2")] == "Mr. Ladd"
    r = RoutingAnalyzer().analyze(corpus)
    assert [(x.author, x.addressee, x.page) for x in r.letters] == [("person:1", "person:2", 1)]   # signature next page
    assert r.org_edges == {("org:4", "org:5"): 1} and corpus.era("D1") == "1950s"
    (inc,) = e.incidents()
    assert inc.doc_ids == ["D1"] and inc.incident_id == 3


def test_partial_dates_as_the_original():
    from uap_geo.replications.common.partial_dates import PartialDate, Precision as P
    d = PartialDate.parse("1949-03-06/07")
    assert (d.start, d.end, d.precision) == (date(1949, 3, 6), date(1949, 3, 7), P.DAY)
    assert PartialDate.parse("1947-11").gap_days(PartialDate.parse("1947-12-03")) == 3
