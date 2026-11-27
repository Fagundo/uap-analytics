"""Lexicon themes: a transparent measure for the questions this project asks of the records.

A theme's value on a page is the share of the page's cleaned words that match the theme's word list.
Matching is by word prefix ('classif' matches classified and classification), so inflections count.
Unlike topics, themes are fixed in advance, so they can be compared across eras and agencies without
the model redrawing them. Words used as page markings ('secret', 'confidential') are removed by the
cleaner and can't inflate the secrecy theme.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from uap_analytics.replications.topics.text import CleanPage


@dataclass(frozen=True)
class Theme:
    name: str
    prefixes: tuple[str, ...]                    # 'classif' -> classified, classification
    exact: frozenset[str] = frozenset()          # whole words only ('press' but not 'pressure')

    def matches(self, word: str) -> bool:
        return word in self.exact or word.startswith(self.prefixes)


THEMES: tuple[Theme, ...] = (
    Theme("secrecy and security", ("secur", "clearanc", "sensitiv", "declassif", "compartment", "withh",
                                   "disseminat", "safeguard", "custod", "confidentiality"),
          frozenset({"access", "cover", "secrecy"})),
    Theme("public relations and the press", ("public", "newspaper", "media", "debunk", "educat",
                                             "hysteri", "panic", "rumor", "rumour", "broadcast", "reporter",
                                             "journalist", "magazine"), frozenset({"press"})),
    Theme("Soviet and foreign technology", ("soviet", "russia", "ussr", "foreign", "german", "missile",
                                            "rocket", "peenemunde", "satellite")),
    Theme("instruments and physical evidence", ("radar", "film", "photograph", "camera", "theodolite",
                                                "instrument", "measur", "sample", "spectr", "telescop",
                                                "recording", "sensor", "infrared", "thermal")),
    Theme("human effects and medicine", ("medical", "blood", "injur", "burn", "health", "symptom",
                                         "physician", "hospital", "radiation", "illness", "nause", "doctor",
                                         "biolog", "physiolog")),
    Theme("fragments and recovery", ("fragment", "debris", "recover", "hardware", "wreckage",
                                     "crash", "remnant", "artifact")),          # not 'materiel' (Air Materiel Command)
    Theme("threat and defense", ("threat", "defens", "hostile", "attack", "intercept", "scramble", "weapon",
                                 "nuclear", "atomic", "invasion")),
    Theme("contracts and funding", ("contract", "fund", "budget", "cost", "proposal", "deliverabl",
                                    "milestone", "purchase", "invoice")),
)


class ThemeScorer:
    def __init__(self, themes: tuple[Theme, ...] = THEMES):
        self.themes = themes

    def score(self, pages: list[CleanPage]) -> np.ndarray:
        """pages x themes: share of each page's words that belong to each theme."""
        out = np.zeros((len(pages), len(self.themes)))
        for i, p in enumerate(pages):
            n = len(p.tokens) or 1
            for j, th in enumerate(self.themes):
                out[i, j] = sum(1 for w in p.tokens if th.matches(w)) / n
        return out

    def words(self, pages: list[CleanPage], top: int = 12) -> list[list[tuple[str, int]]]:
        """The words that actually carry each theme in this corpus (to check the lexicon's reach)."""
        from collections import Counter
        out = []
        for th in self.themes:
            c = Counter(w for p in pages for w in p.tokens if th.matches(w))
            out.append(c.most_common(top))
        return out
