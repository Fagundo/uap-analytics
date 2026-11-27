"""Communities of people and organizations, tested against a null model (replication; unchanged method).

1. Co-mention: two entities are tied by the pages they share. Each shared page adds 1/(n-1), where
   n is the number of entities on that page (Newman's weighting), so crowded pages such as rosters
   and distribution lists count for less.
2. Null model: within every document, pages are re-dealt at random. Each entity keeps how many pages
   it appears on in that document, and each page keeps its number of entities. A tie is *significant*
   when the pair shares more pages than in at least (1 - alpha) of the null runs. This asks: do they
   appear on the same pages more than chance, given that they are in the same documents? Big files
   like D017 or D180 can't manufacture ties on their own.
3. Communities: Louvain on the graph of significant ties only (fixed seed, reproducible). Each
   community is described by the documents its *internal significant ties* come from, so a loosely
   attached member can't add an agency or era on its own.
4. Stability: Louvain is rerun with other seeds; a community's stability is the share of its member
   pairs that stay in one community across those runs. Low stability means the grouping is fragile.
"""
from __future__ import annotations

import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from itertools import combinations

from uap_analytics.replications.networks.corpus import EntityCorpus, NodeId, PageId


@dataclass(frozen=True)
class Tie:
    a: NodeId
    b: NodeId
    pages: int                         # shared pages, observed
    weight: float                      # Newman weight
    null_mean: float                   # mean shared pages across null runs
    p_value: float                     # share of null runs with >= observed shared pages
    docs: tuple[str, ...]


@dataclass
class Community:
    id: int
    members: list[NodeId]              # strongest first
    strength: dict[NodeId, float]
    docs: Counter                      # doc -> internal shared pages
    agencies: list[str]
    eras: list[str]
    evidence: list[PageId]             # pages where most members appear together
    internal_ties: int
    stability: float = 1.0

    @property
    def cross_agency(self) -> bool:
        return len(self.agencies) > 1


@dataclass
class CommunityResult:
    ties: list[Tie]
    communities: list[Community]
    tested_pairs: int
    null_runs: int
    alpha: float
    modularity: float
    stats: dict = field(default_factory=dict)


class PageShuffleNull:
    """Re-deal pages within each document, keeping per-document entity counts and page sizes."""

    def __init__(self, pages: dict[PageId, set[NodeId]], rng: random.Random):
        self._by_doc: dict[str, list[tuple[PageId, int]]] = defaultdict(list)
        self._tokens: dict[str, list[NodeId]] = defaultdict(list)
        for (doc, page), nodes in sorted(pages.items()):              # sorted: reproducible across runs
            self._by_doc[doc].append(((doc, page), len(nodes)))
            self._tokens[doc].extend(sorted(nodes))
        self._rng = rng

    def sample(self) -> dict[PageId, set[NodeId]]:
        out: dict[PageId, set[NodeId]] = {}
        for doc, slots in sorted(self._by_doc.items()):
            tokens = self._tokens[doc][:]
            self._rng.shuffle(tokens)
            i = 0
            for page, size in slots:
                out[page] = set(tokens[i:i + size])     # a rare repeat on one page collapses
                i += size
        return out


class CommunityAnalyzer:
    def __init__(self, null_runs: int = 500, alpha: float = 0.01, min_pages: int = 2, seed: int = 7,
                 resolution: float = 1.0, include_placeholders: bool = True, stability_runs: int = 25):
        self.null_runs, self.alpha, self.min_pages = null_runs, alpha, min_pages
        self.stability_runs = stability_runs
        self.seed, self.resolution, self.include_placeholders = seed, resolution, include_placeholders

    # ------------------------------------------------------------------ ties
    def _pages(self, corpus: EntityCorpus) -> dict[PageId, set[NodeId]]:
        keep = {n for n, info in corpus.nodes.items() if self.include_placeholders or not info.placeholder}
        return {p: {n for n in ns if n in keep} for p, ns in corpus.pages.items() if len(ns & keep) >= 2}

    @staticmethod
    def _shared(pages: dict[PageId, set[NodeId]]) -> tuple[Counter, dict[tuple, float], dict[tuple, set[str]]]:
        counts: Counter = Counter()
        weights: dict[tuple, float] = defaultdict(float)
        docs: dict[tuple, set[str]] = defaultdict(set)
        for page, nodes in pages.items():
            if len(nodes) < 2:
                continue
            w = 1.0 / (len(nodes) - 1)
            for a, b in combinations(sorted(nodes), 2):
                counts[(a, b)] += 1
                weights[(a, b)] += w
                docs[(a, b)].add(page[0])
        return counts, weights, docs

    def ties(self, corpus: EntityCorpus) -> tuple[list[Tie], int]:
        pages = self._pages(corpus)
        observed, weights, docs = self._shared(pages)
        tested = {pair: c for pair, c in observed.items() if c >= self.min_pages}
        ge = Counter()
        total = Counter()
        null = PageShuffleNull(pages, random.Random(self.seed))
        for _ in range(self.null_runs):
            sample = null.sample()
            seen: Counter = Counter()
            for nodes in sample.values():
                if len(nodes) < 2:
                    continue
                for pair in combinations(sorted(nodes), 2):
                    if pair in tested:
                        seen[pair] += 1
            for pair, c in tested.items():
                s = seen.get(pair, 0)
                total[pair] += s
                if s >= c:
                    ge[pair] += 1
        out = []
        for pair, c in tested.items():
            p = (ge[pair] + 1) / (self.null_runs + 1)
            out.append(Tie(pair[0], pair[1], c, round(weights[pair], 4), round(total[pair] / self.null_runs, 3),
                           round(p, 4), tuple(sorted(docs[pair]))))
        return sorted(out, key=lambda t: (t.p_value, -t.pages)), len(tested)

    # ------------------------------------------------------------------ communities
    def analyze(self, corpus: EntityCorpus) -> CommunityResult:
        import networkx as nx
        ties, tested = self.ties(corpus)
        sig = [t for t in ties if t.p_value <= self.alpha]
        g = nx.Graph()
        for t in sorted(sig, key=lambda t: (t.a, t.b)):
            g.add_edge(t.a, t.b, weight=t.weight)
        parts = nx.community.louvain_communities(g, weight="weight", resolution=self.resolution,
                                                 seed=self.seed) if g.number_of_edges() else []
        modularity = nx.community.modularity(g, parts, weight="weight") if parts else 0.0
        pages = self._pages(corpus)
        reruns = [nx.community.louvain_communities(g, weight="weight", resolution=self.resolution, seed=self.seed + k)
                  for k in range(1, self.stability_runs + 1)] if parts else []
        communities = [self._describe(i, sorted(part), g, sig, pages, corpus, reruns)
                       for i, part in enumerate(sorted(parts, key=len, reverse=True), start=1) if len(part) >= 3]
        return CommunityResult(ties=sig, communities=communities, tested_pairs=tested, null_runs=self.null_runs,
                               alpha=self.alpha, modularity=round(modularity, 3),
                               stats={"nodes_with_ties": g.number_of_nodes(), "significant_ties": len(sig)})

    @staticmethod
    def _stability(members: list[NodeId], reruns: list[list[set]]) -> float:
        if not reruns or len(members) < 2:
            return 1.0
        pairs = list(combinations(members, 2))
        together = 0
        for parts in reruns:
            where = {n: i for i, part in enumerate(parts) for n in part}
            together += sum(1 for a, b in pairs if where.get(a) == where.get(b))
        return round(together / (len(pairs) * len(reruns)), 3)

    def _describe(self, cid: int, members: list[NodeId], g, sig: list[Tie], pages, corpus: EntityCorpus,
                  reruns: list[list[set]]) -> Community:
        mset = set(members)
        strength = {m: round(sum(d["weight"] for _, n, d in g.edges(m, data=True) if n in mset), 3) for m in members}
        internal = [t for t in sig if t.a in mset and t.b in mset]
        docs: Counter = Counter(d for t in internal for d in t.docs)
        best = sorted(pages, key=lambda p: (-len(pages[p] & mset), p))[:5]
        return Community(
            id=cid, members=sorted(members, key=lambda m: -strength[m]), strength=strength, docs=docs,
            agencies=sorted({corpus.agency(d) for d in docs}), eras=sorted({corpus.era(d) for d in docs}),
            evidence=[p for p in best if len(pages[p] & mset) >= 2], internal_ties=len(internal),
            stability=self._stability(members, reruns))
