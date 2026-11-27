"""The three replications: each runs the original test on the export's inputs and returns its full output."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter

from uap_analytics.replications.bluebook.index import OFFICIAL_SOURCE, coverage
from uap_analytics.replications.bluebook.shift import PREDICATES, ShareShiftTest
from uap_analytics.replications.common.geo import haversine_km
from uap_analytics.replications.common.stats import benjamini_hochberg
from uap_analytics.replications.inputs import ReplicationInputs
from uap_analytics.replications.nuclear.sites import group_sites
from uap_analytics.replications.nuclear.window import EventWindowTest, SiteEvent
from uap_analytics.replications.programs.shuffle import CoincidenceTest, ProximityTest
from uap_analytics.replications.programs.sightings import one_per
from uap_analytics.replications.programs.trend import local_share_by_year, program_sites

NUCLEAR_SOURCE = ("Yang, North, Romney & Richards, Worldwide Nuclear Explosions (IASPEI handbook), via the "
                  "richgel999/ufo_data conversion")


class Replication(ABC):
    name = ""
    title = ""

    @abstractmethod
    def run(self, inputs: ReplicationInputs) -> dict:
        """The test's full output (the original command's JSON, without report text)."""


class ProgramsReplication(Replication):
    """Shuffle tests of sightings against flight programs (originally ``pursue programs``)."""
    name = "programs"
    title = "Do sightings cluster near classified flight programs in space and time?"
    CATALOGS = ("hatch", "hatch:BBK", "nicap", "bluebook-unknowns", "magonia")

    def __init__(self, radius_km: float = 300.0, shuffles: int = 10000):
        self.radius, self.shuffles = radius_km, shuffles

    def run(self, inputs: ReplicationInputs) -> dict:
        sets = {}
        found = inputs.pursue_sightings()
        sets["pursue"] = found
        sets["pursue, one per document+state+year"] = one_per(found, lambda s: (s.group, s.state, s.date.start.year))
        for spec in self.CATALOGS:
            source, _, flag = spec.partition(":")
            found = inputs.external_sightings(source, require_flag=flag or None)
            sets[spec] = found
            sets[f"{spec}, one per state+month"] = one_per(found, lambda s: (s.state, s.date.start.year, s.date.start.month))
        catalog = inputs.programs()
        tests = [CoincidenceTest(catalog, shuffles=self.shuffles),
                 ProximityTest(catalog, radius_km=self.radius, shuffles=self.shuffles)]
        results = [r for name, ss in sets.items() for t in tests for r in [t.run(name, ss)] if r.sightings]
        sites = program_sites(catalog)
        trends = {name: local_share_by_year(ss, sites, self.radius) for name, ss in sets.items()
                  if any(s.lat is not None for s in ss)}
        return {"tests": [r.to_dict() for r in results], "local_share_by_year": trends}


class NuclearReplication(Replication):
    """Reports in the days after nuclear tests, by test site and kind (originally ``pursue nuclear``)."""
    name = "nuclear"
    title = "Do UFO reports rise in the days after nuclear tests?"
    CATALOGS = ("hatch", "nicap", "bluebook-unknowns")

    def __init__(self, radius_km: float = 600.0, min_tests: int = 10, site_radius_km: float = 150.0,
                 shuffles: int = 2000):
        self.radius, self.min_tests, self.site_radius, self.shuffles = radius_km, min_tests, site_radius_km, shuffles

    def run(self, inputs: ReplicationInputs) -> dict:
        sites = group_sites(inputs.nuclear_tests(), self.site_radius)
        catalogs = {}
        for source in self.CATALOGS:
            world = inputs.external_sightings(source, world=True)
            catalogs[source] = world if world else inputs.external_sightings(source)
        results, rows = [], []
        for site in sites:
            for kind in ("air", "underground"):
                events = [SiteEvent(t.day, t.lat, t.lon, t.name) for t in site.tests if t.kind == kind]
                if len(events) < self.min_tests:
                    continue
                label = f"{site.label}, {kind} ({len(events)} tests, {events[0].day.year}-{events[-1].day.year})"
                for source, found in catalogs.items():
                    located = any(s.lat is not None for s in found)
                    for r in ([None, self.radius] if located else [None]):
                        for w in (0, 2):
                            res = EventWindowTest(window_days=w, radius_km=r, shuffles=self.shuffles,
                                                  center=(site.lat, site.lon)).run(source, label, events, found)
                            if res.sightings and res.covered_days:
                                results.append(res)
                                rows.append({"site": site.label, "country": site.country, "kind": kind})
        qs = benjamini_hochberg([r.p_value for r in results]) if results else []
        out = [{**row, **r.to_dict(), "q_value": round(q, 4)} for row, r, q in zip(rows, results, qs)]
        return {"tests_source": NUCLEAR_SOURCE,
                "sites": [{"id": s.id, "label": s.label, "country": s.country, "lat": s.lat, "lon": s.lon,
                           "tests": len(s.tests)} for s in sites],
                "results": out}


class BlueBookReplication(Replication):
    """Did Blue Book's conclusions shift when the spy planes began flying? (originally ``pursue bluebook``)"""
    name = "bluebook"
    title = "Did Blue Book's conclusions shift when the spy planes began flying, and where?"

    def __init__(self, region_km: float = 900.0, window: int = 24):
        self.region_km, self.window = region_km, window

    def run(self, inputs: ReplicationInputs) -> dict:
        rows = inputs.bluebook_index()
        placer = inputs.placer
        aircraft = [p for p in inputs.programs() if p.kind == "aircraft" and p.sites and 1949 <= p.start.year <= 1967]
        aircraft.sort(key=lambda p: p.start)
        by_year = {}
        for r in rows:
            by_year.setdefault(r.year, Counter())[r.category] += 1
        report = {"coverage": coverage(rows), "official_totals_source": OFFICIAL_SOURCE,
                  "by_year": {str(y): dict(c) for y, c in sorted(by_year.items())},
                  "families": dict(Counter(r.family for r in rows if r.family).most_common()), "tests": []}
        states_seen = {r.state for r in rows if r.state}
        for p in aircraft:
            site = p.sites[0]
            region = sorted(s for s in states_seen if placer.centroid(s)
                            and haversine_km(*placer.centroid(s), site.lat, site.lon) <= self.region_km)
            test = ShareShiftTest(rows, set(region), self.window)
            for label, pred in PREDICATES.items():
                res = test.run(label, pred, p.start.year, p.start.month)
                report["tests"].append({"program": p.id, "site": site.name, "region": region, **res.to_dict()})
        return report


class NetworksReplication(Replication):
    """Who writes to whom, and tested communities (originally ``pursue networks``)."""
    name = "networks"
    title = "Who writes to whom in the released documents, and which names cluster beyond chance?"

    def __init__(self, null_runs: int = 500, alpha: float = 0.01):
        self.null_runs, self.alpha = null_runs, alpha

    def run(self, inputs: ReplicationInputs) -> dict:
        from uap_analytics.replications.networks.communities import CommunityAnalyzer
        from uap_analytics.replications.networks.report import NetworkReport
        from uap_analytics.replications.networks.routing import RoutingAnalyzer
        corpus = inputs.entities.corpus()
        return NetworkReport().build(corpus, RoutingAnalyzer().analyze(corpus),
                                     CommunityAnalyzer(null_runs=self.null_runs, alpha=self.alpha).analyze(corpus))


class TopicsReplication(Replication):
    """Topics, lexicon themes and their tested differences by era and agency (originally ``pursue topics``)."""
    name = "topics"
    title = "What do the released documents talk about, and how does it differ by era and agency?"

    def run(self, inputs: ReplicationInputs) -> dict:
        from uap_analytics.replications.topics.report import TopicLabeler, TopicReport
        labels = inputs.entities.dataset("topic_labels.json").get("labels", [])
        return TopicReport(labeler=TopicLabeler(labels)).build(inputs.entities.documents(), inputs.entities.pages())


class ClaimsReplication(Replication):
    """Explanations offered for famous cases, checked against physics (originally ``pursue claims --screen``)."""
    name = "claims"
    title = "Do the explanations offered for famous cases fit their own stated facts?"

    def run(self, inputs: ReplicationInputs) -> dict:
        from uap_analytics.replications.claims.catalog import parse_catalog
        from uap_analytics.replications.claims.report import ClaimReport
        from uap_analytics.replications.claims.screen import SkyScreen
        cases, claims = parse_catalog(inputs.entities.dataset("case_claims.json"))
        return ClaimReport().build(cases, claims, inputs.entities.incidents(), SkyScreen())


REPLICATIONS = {r.name: r for r in (ProgramsReplication, NuclearReplication, BlueBookReplication,
                                    NetworksReplication, TopicsReplication, ClaimsReplication)}
