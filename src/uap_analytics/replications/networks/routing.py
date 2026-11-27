"""Who writes to whom.

A directed edge author -> addressee is recorded when a person is tagged as an addressee on a page and another
person as an author on that page or the next (signatures fall over page breaks). Edges are lifted to
organizations through each person's stated affiliation. This measures routing as preserved in these releases.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field

from uap_analytics.replications.networks.corpus import EntityCorpus, NodeId, PageId


@dataclass(frozen=True)
class Letter:
    doc_id: str
    page: int
    author: NodeId
    addressee: NodeId
    author_quote: str
    addressee_quote: str


@dataclass
class RoutingResult:
    letters: list[Letter]
    edges: Counter                                     # (author, addressee) -> letters
    org_edges: Counter                                 # (author org, addressee org) -> letters
    received: Counter = field(default_factory=Counter)
    sent: Counter = field(default_factory=Counter)

    def correspondents(self, node: NodeId) -> tuple[set[NodeId], set[NodeId]]:
        senders = {a for (a, b) in self.edges if b == node}
        recipients = {b for (a, b) in self.edges if a == node}
        return senders, recipients


class RoutingAnalyzer:
    def __init__(self, signature_window: int = 1):
        self.window = signature_window

    def analyze(self, corpus: EntityCorpus) -> RoutingResult:
        authors: dict[PageId, set[NodeId]] = defaultdict(set)
        addressees: dict[PageId, set[NodeId]] = defaultdict(set)
        for (page, node), roles in corpus.roles.items():
            if not node.startswith("person:"):
                continue
            if "author" in roles:
                authors[page].add(node)
            if "addressee" in roles:
                addressees[page].add(node)
        letters: dict[tuple, Letter] = {}
        for (doc, p), tos in addressees.items():
            for offset in range(self.window + 1):
                for frm in authors.get((doc, p + offset), ()):
                    for to in tos:
                        if frm == to or (doc, p, frm, to) in letters:
                            continue
                        letters[(doc, p, frm, to)] = Letter(
                            doc, p, frm, to, corpus.quotes.get(((doc, p + offset), frm), ""),
                            corpus.quotes.get(((doc, p), to), ""))
        result = RoutingResult(letters=sorted(letters.values(), key=lambda x: (x.doc_id, x.page, x.author, x.addressee)),
                               edges=Counter(), org_edges=Counter())
        for x in result.letters:
            result.edges[(x.author, x.addressee)] += 1
            result.sent[x.author] += 1
            result.received[x.addressee] += 1
            fa, ta = corpus.nodes[x.author].affiliation_org, corpus.nodes[x.addressee].affiliation_org
            if fa and ta and fa != ta:
                result.org_edges[(fa, ta)] += 1
        return result
