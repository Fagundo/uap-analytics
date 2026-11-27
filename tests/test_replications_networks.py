"""Networks replication: routing, the page re-deal null, community ties (ported with the code)."""
import random

from uap_analytics.replications.networks.communities import CommunityAnalyzer, PageShuffleNull
from uap_analytics.replications.networks.corpus import DocumentInfo, EntityCorpus, MentionRow, NodeInfo
from uap_analytics.replications.networks.report import NetworkReport
from uap_analytics.replications.networks.routing import RoutingAnalyzer

PEOPLE = [NodeInfo("person:1", "person", 1, "John A. Samford", affiliation_org="org:1"),
          NodeInfo("person:2", "person", 2, "Joseph A. Bloomer", affiliation_org="org:2"),
          NodeInfo("person:3", "person", 3, "E. C. Welsh")]
ORGS = [NodeInfo("org:1", "org", 1, "United States Air Force"), NodeInfo("org:2", "org", 2, "ATIC")]


def _m(pid, doc, page, role=None, raw="x"):
    return MentionRow(doc, page, "person", pid, role, raw)


def test_addressee_with_author_on_same_or_next_page():
    mentions = [_m(1, "D095", 2, "addressee", "Major General John A. Samford"),
                _m(2, "D095", 3, "author", "JOSEPH A. BLOOMER"),           # signature over the page break
                _m(3, "D095", 7, "author")]                                # too far away
    c = EntityCorpus.build([DocumentInfo("D095", "DOW", "1955")], PEOPLE + ORGS, mentions)
    r = RoutingAnalyzer().analyze(c)
    assert [(x.author, x.addressee, x.page) for x in r.letters] == [("person:2", "person:1", 2)]
    assert r.org_edges == {("org:2", "org:1"): 1}


def _corpus():
    """Persons 1 and 2 share every page they appear on; person 3 is spread out in the same document."""
    mentions = [_m(3, "D1", p) for p in range(1, 9)]
    for p in (1, 2, 3, 4):
        mentions += [_m(1, "D1", p), _m(2, "D1", p)]
    mentions += [_m(9, "D1", p) for p in (5, 6, 7, 8)]                    # filler entity
    people = [*PEOPLE, NodeInfo("person:9", "person", 9, "Filler Person")]
    return EntityCorpus.build([DocumentInfo("D1", "DOW", "1955")], people, mentions)


def test_null_preserves_page_sizes_and_counts():
    pages = {("D1", 1): {"a", "b"}, ("D1", 2): {"a", "c", "d"}, ("D2", 1): {"e", "f"}}
    s = PageShuffleNull(pages, random.Random(1)).sample()
    assert s[("D2", 1)] == {"e", "f"}                                     # never crosses documents
    assert sorted(len(v) for k, v in s.items() if k[0] == "D1") == [2, 3]


def test_always_together_pair_is_significant_and_reproducible():
    a = CommunityAnalyzer(null_runs=200, alpha=0.05).ties(_corpus())[0]
    assert a == CommunityAnalyzer(null_runs=200, alpha=0.05).ties(_corpus())[0]
    top = a[0]
    assert (top.a, top.b, top.pages) == ("person:1", "person:2", 4) and top.p_value < 0.05
    spread = next(t for t in a if {t.a, t.b} == {"person:1", "person:3"})
    assert spread.p_value > 0.05


def test_report_is_json_ready():
    c = _corpus()
    rep = NetworkReport().build(c, RoutingAnalyzer().analyze(c), CommunityAnalyzer(null_runs=50).analyze(c))
    assert "communities" in rep["communities"] and rep["routing"]["letters_total"] == 0
