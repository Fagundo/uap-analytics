"""Run the topic and theme analyses end to end and serialize them (replication; unchanged method)."""
from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

import numpy as np

from uap_analytics.replications.networks.corpus import DocumentInfo, PageText, era
from uap_analytics.replications.topics.model import Difference, PrevalenceAnalyzer, Topic, TopicModeler
from uap_analytics.replications.topics.text import PageCleaner
from uap_analytics.replications.topics.themes import ThemeScorer


class TopicLabeler:
    """Apply human labels to topics whose top words contain all of a label's key words."""

    def __init__(self, rules: list[dict] | None = None):
        self.rules = rules or []

    @classmethod
    def from_file(cls, path: Path | None) -> TopicLabeler:
        if path is None or not path.exists():
            return cls()
        return cls(json.loads(path.read_text()).get("labels", []))

    def label(self, topic: Topic) -> str | None:
        words = set(topic.words)
        return next((r["label"] for r in self.rules if set(r["words"]) <= words), None)


class TopicReport:
    def __init__(self, cleaner: PageCleaner | None = None, modeler: TopicModeler | None = None,
                 themes: ThemeScorer | None = None, prevalence: PrevalenceAnalyzer | None = None,
                 labeler: TopicLabeler | None = None, min_pages: int = 100):
        self.min_pages = min_pages
        self.cleaner = cleaner or PageCleaner()
        self.modeler = modeler or TopicModeler()
        self.themes = themes or ThemeScorer()
        self.prevalence = prevalence or PrevalenceAnalyzer()
        self.labeler = labeler or TopicLabeler()

    def build(self, documents: Iterable[DocumentInfo], pages: Iterable[PageText]) -> dict:
        docs = {d.doc_id: d for d in documents}
        eras = {d: era(x.doc_date) for d, x in docs.items()}
        agencies = {d: x.agency for d, x in docs.items()}
        reference = {d for d, e in eras.items() if e in ("2000s-10s", "2016+")}      # born-digital texts
        clean = self.cleaner.clean(pages, reference, {d: x.release for d, x in docs.items()})
        if len(clean) < self.min_pages:
            raise ValueError(f"too few usable pages for topic modeling ({len(clean)} < {self.min_pages})")
        model = self.modeler.fit(clean)
        theme_matrix = self.themes.score(clean)
        theme_words = self.themes.words(clean)

        def measures(matrix: np.ndarray) -> dict:
            return {
                "by_era": self.prevalence.table(model.pages, matrix, eras),
                "by_agency": self.prevalence.table(model.pages, matrix, agencies),
                "differences": [self._diff(d) for axis, lab in (("era", eras), ("agency", agencies))
                                for d in self.prevalence.differences(model.pages, matrix, axis, lab)
                                if d.significant],
            }

        return {
            "method": {"pages": len(clean), "fit_pages": model.fit_pages, "k": model.k,
                       "stability": {str(k): v for k, v in model.stability.items()},
                       "permutations": self.prevalence.permutations, "fdr": self.prevalence.fdr},
            "topics": [{"id": t.id, "label": self.labeler.label(t), "words": t.words, "weights": t.weights,
                        "typical": [{"doc": d, "page": p, "share": s, "snippet": sn} for d, p, s, sn in t.typical]}
                       for t in model.topics],
            "topic_prevalence": measures(model.shares),
            "themes": [{"id": i + 1, "name": th.name, "words": [w for w, _ in ws]}
                       for i, (th, ws) in enumerate(zip(self.themes.themes, theme_words))],
            "theme_prevalence": measures(theme_matrix),
        }

    @staticmethod
    def _diff(d: Difference) -> dict:
        return {"measure": d.measure, "axis": d.axis, "group": d.group, "docs": d.docs,
                "group_value": d.group_share, "rest_value": d.rest_share, "lift": d.lift, "p": d.p, "q": d.q,
                "drivers": [{"doc": doc, "value": v} for doc, v in d.drivers],
                "lift_without_top": d.lift_without_top, "robust": bool(d.robust)}
