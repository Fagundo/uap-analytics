"""Topics across pages, and a significance test for how any page measure differs by era or agency.

Model (``TopicModeler``):
  * TF-IDF over cleaned pages (``text.PageCleaner``): words on 5+ pages and on at most 40% of pages.
  * Balanced fit: NMF is fit on at most ``pages_per_doc`` pages from each document and at most
    ``pages_per_group`` from each collection (fixed random samples), so neither one 298-page personnel
    file nor 575 one-page FAA reports can claim several topics. Every page is then scored.
  * Number of topics by stability: for each candidate k, NMF is fit from several random starts and
    topics are matched across runs (Hungarian matching, cosine of word weights). The k whose topics
    reproduce best is kept; ties go to the smaller k.

Prevalence (``PrevalenceAnalyzer``), used for topics and lexicon themes alike:
  * A document's share of a measure is the mean over its pages, so each document counts once. Only
    documents with a known era (or agency) take part in that axis's tests.
  * For each measure and each era or agency with 3+ documents (and 3+ outside it), the difference
    between the group's mean and everyone else's is tested by shuffling labels across *documents*.
    P-values are corrected across all tests (Benjamini-Hochberg). Differences with q <= 0.10 are
    reported as significant.
  * Robustness: each difference names its driving documents and its lift with the top one removed.
    A difference that falls below 1.5x without one document rests on that document.
"""
from __future__ import annotations

import random
import re
from collections import defaultdict
from dataclasses import dataclass, field

import numpy as np

from uap_analytics.replications.topics.text import CleanPage

PageId = tuple[str, int]


@dataclass
class Topic:
    id: int
    words: list[str]
    weights: list[float]
    typical: list[tuple[str, int, float, str]] = field(default_factory=list)   # doc, page, share, snippet


@dataclass
class TopicModel:
    topics: list[Topic]
    pages: list[PageId]
    shares: np.ndarray                          # pages x topics, rows sum to 1
    k: int
    stability: dict[int, float]                 # candidate k -> mean matched cosine across random starts
    fit_pages: int


class TopicModeler:
    def __init__(self, k_candidates: tuple[int, ...] = (8, 10, 12, 14, 16, 18), stability_runs: int = 5,
                 pages_per_doc: int = 30, top_words: int = 15, seed: int = 11, min_pages: int = 5,
                 max_share: float = 0.4, pages_per_group: int = 300):
        self.k_candidates, self.stability_runs, self.pages_per_doc = k_candidates, stability_runs, pages_per_doc
        self.pages_per_group = pages_per_group
        self.top_words, self.seed, self.min_pages, self.max_share = top_words, seed, min_pages, max_share

    def _balanced(self, pages: list[CleanPage]) -> list[int]:
        rng = random.Random(self.seed)
        by_doc: dict[str, list[int]] = defaultdict(list)
        for i, p in enumerate(pages):
            by_doc[p.doc_id].append(i)
        per_group: dict[str, list[int]] = defaultdict(list)
        for doc in sorted(by_doc):
            idx = by_doc[doc]
            chosen = idx if len(idx) <= self.pages_per_doc else sorted(rng.sample(idx, self.pages_per_doc))
            per_group[pages[idx[0]].group].extend(chosen)
        picked = []
        for g in sorted(per_group):              # and at most pages_per_group from one collection
            idx = per_group[g]
            picked += idx if len(idx) <= self.pages_per_group else sorted(rng.sample(idx, self.pages_per_group))
        return sorted(picked)

    def _stability(self, x, k: int) -> float:
        from scipy.optimize import linear_sum_assignment
        from sklearn.decomposition import NMF
        hs = []
        for s in range(self.stability_runs):
            h = NMF(n_components=k, init="random", random_state=self.seed + 100 * s, max_iter=600).fit(x).components_
            hs.append(h / (np.linalg.norm(h, axis=1, keepdims=True) + 1e-12))
        sims = []
        for i in range(len(hs)):
            for j in range(i + 1, len(hs)):
                c = hs[i] @ hs[j].T
                r, cidx = linear_sum_assignment(-c)
                sims.append(float(c[r, cidx].mean()))
        return round(float(np.mean(sims)), 3)

    def fit(self, pages: list[CleanPage]) -> TopicModel:
        from sklearn.decomposition import NMF
        from sklearn.feature_extraction.text import TfidfVectorizer
        fit_idx = self._balanced(pages)
        vec = TfidfVectorizer(analyzer=lambda toks: toks, min_df=self.min_pages, max_df=self.max_share,
                              sublinear_tf=True)
        x_fit = vec.fit_transform([pages[i].tokens for i in fit_idx])
        vocab = vec.get_feature_names_out()
        stability = {k: self._stability(x_fit, k) for k in self.k_candidates}
        k = max(stability, key=lambda kk: (stability[kk], -kk))
        nmf = NMF(n_components=k, init="nndsvda", random_state=self.seed, max_iter=800).fit(x_fit)
        h = nmf.components_
        w = nmf.transform(vec.transform([p.tokens for p in pages]))
        shares = w / (w.sum(axis=1, keepdims=True) + 1e-12)
        topics = []
        for t in range(k):
            order = np.argsort(-h[t])[:self.top_words]
            words = [str(vocab[i]) for i in order]
            topics.append(Topic(t + 1, words, [round(float(h[t, i]), 4) for i in order],
                                _typical(t, pages, shares, words)))
        return TopicModel(topics, [p.id for p in pages], shares, k, stability, len(fit_idx))


def _typical(t: int, pages: list[CleanPage], shares: np.ndarray, words: list[str], n: int = 6,
             per_doc: int = 2) -> list[tuple[str, int, float, str]]:
    out, per = [], defaultdict(int)
    top = set(words[:8])
    for i in np.argsort(-shares[:, t]):
        p = pages[i]
        if per[p.doc_id] >= per_doc:
            continue
        per[p.doc_id] += 1
        out.append((p.doc_id, p.page, round(float(shares[i, t]), 3), snippet(p.text, top)))
        if len(out) >= n:
            break
    return out


def snippet(text: str, words: set[str], width: int = 220) -> str:
    """The stretch of the page densest in the given words."""
    flat = " ".join(text.split())
    hits = [m.start() for m in re.finditer(r"[A-Za-z]+", flat) if m.group().lower() in words]
    if not hits:
        return flat[:width]
    best = max(hits, key=lambda s: sum(1 for h in hits if s <= h < s + width))
    start = max(0, best - 20)
    return ("…" if start else "") + flat[start:start + width] + "…"


@dataclass(frozen=True)
class Difference:
    measure: int                                 # column index + 1 (topic id or theme number)
    axis: str                                    # era | agency
    group: str
    group_share: float                           # mean document value inside the group
    rest_share: float
    lift: float                                  # group mean / overall document mean
    p: float
    q: float
    docs: int
    drivers: tuple[tuple[str, float], ...] = ()  # the group's documents with the highest values
    lift_without_top: float | None = None        # lift after dropping the top driver: does one file carry it?

    @property
    def significant(self) -> bool:
        return self.q <= 0.10

    @property
    def robust(self) -> bool:
        """Still at least 1.5x (or at most 0.67x) the overall rate without its top document."""
        if self.lift_without_top is None:
            return False
        return self.lift_without_top >= 1.5 if self.lift >= 1 else self.lift_without_top <= 0.67


class PrevalenceAnalyzer:
    def __init__(self, permutations: int = 2000, min_docs: int = 3, fdr: float = 0.10, seed: int = 5):
        self.permutations, self.min_docs, self.fdr, self.seed = permutations, min_docs, fdr, seed

    @staticmethod
    def document_values(pages: list[PageId], matrix: np.ndarray) -> tuple[list[str], np.ndarray]:
        rows: dict[str, list[int]] = defaultdict(list)
        for i, (doc, _) in enumerate(pages):
            rows[doc].append(i)
        docs = sorted(rows)
        return docs, np.vstack([matrix[rows[d]].mean(axis=0) for d in docs])

    def table(self, pages: list[PageId], matrix: np.ndarray, labels: dict[str, str]) -> dict[str, dict]:
        docs, s = self.document_values(pages, matrix)
        groups: dict[str, list[int]] = defaultdict(list)
        for i, d in enumerate(docs):
            groups[labels.get(d, "?")].append(i)
        return {g: {"docs": len(idx), "values": [round(float(v), 4) for v in s[idx].mean(axis=0)]}
                for g, idx in sorted(groups.items())}

    UNKNOWN = ("?", "undated")

    def differences(self, pages: list[PageId], matrix: np.ndarray, axis: str,
                    labels: dict[str, str]) -> list[Difference]:
        """Only documents with a known label take part: an undated document is neither in an era nor in
        the comparison group, so a large undated collection can't drag every era's baseline."""
        docs, s = self.document_values(pages, matrix)
        known = [i for i, d in enumerate(docs) if labels.get(d, "?") not in self.UNKNOWN]
        docs, s = [docs[i] for i in known], s[known]
        lab = np.array([labels.get(d, "?") for d in docs])
        groups = [g for g in sorted(set(lab)) if self.min_docs <= (lab == g).sum() <= len(lab) - self.min_docs]
        observed = {g: s[lab == g].mean(axis=0) - s[lab != g].mean(axis=0) for g in groups}
        exceed = {g: np.zeros(s.shape[1]) for g in groups}
        rng = random.Random(self.seed)
        perm = list(lab)
        for _ in range(self.permutations):
            rng.shuffle(perm)                                             # labels move between documents
            pa = np.array(perm)
            for g in groups:
                d = s[pa == g].mean(axis=0) - s[pa != g].mean(axis=0)
                exceed[g] += np.abs(d) >= np.abs(observed[g]) - 1e-12
        tests = [(g, t, (exceed[g][t] + 1) / (self.permutations + 1)) for g in groups for t in range(s.shape[1])]
        qs = benjamini_hochberg([p for _, _, p in tests])
        overall = s.mean(axis=0)
        out = []
        for (g, t, p), q in zip(tests, qs):
            gs, rs = float(s[lab == g, t].mean()), float(s[lab != g, t].mean())
            members = [(docs[i], float(s[i, t])) for i in np.where(lab == g)[0]]
            ranked = sorted(members, key=lambda x: -x[1] if gs >= rs else x[1])
            drivers = tuple((d, round(val, 4)) for d, val in ranked[:3])
            rest_vals = [val for _, val in ranked[1:]]
            lw = round(float(np.mean(rest_vals) / overall[t]), 2) if rest_vals and overall[t] else None
            out.append(Difference(t + 1, axis, g, round(gs, 4), round(rs, 4),
                                  round(float(gs / overall[t]), 2) if overall[t] else 0.0, round(float(p), 4),
                                  round(float(q), 4), int((lab == g).sum()), drivers, lw))
        return sorted(out, key=lambda d: (d.q, -abs(d.group_share - d.rest_share)))


def benjamini_hochberg(ps: list[float]) -> list[float]:
    n = len(ps)
    order = sorted(range(n), key=lambda i: ps[i])
    q = [0.0] * n
    running = 1.0
    for rank, i in reversed(list(enumerate(order, start=1))):
        running = min(running, ps[i] * n / rank)
        q[i] = running
    return q
