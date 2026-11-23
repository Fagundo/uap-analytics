"""A read-only view of who appears on which page, shared by the network analyses."""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field

NodeId = str                                    # "person:12", "org:7"
PageId = tuple[str, int]                        # (doc_id, page)


def era(doc_date: str | None) -> str:
    """The era of a document's date, as the original analyses grouped them."""
    m = re.match(r"(\d{4})", doc_date or "")
    if not m:
        return "undated"
    y = int(m.group(1))
    return ("1940s" if y < 1950 else "1950s" if y < 1960 else "1960s-70s" if y < 1980
            else "2000s-10s" if y < 2016 else "2016+")


@dataclass(frozen=True)
class NodeInfo:
    id: NodeId
    kind: str                                   # person | org
    entity_id: int
    name: str
    placeholder: bool = False
    affiliation_org: NodeId | None = None       # person -> the organization their affiliation names


@dataclass(frozen=True)
class DocumentInfo:
    doc_id: str
    agency: str
    doc_date: str | None
    release: str = ""


@dataclass(frozen=True)
class MentionRow:
    doc_id: str
    page: int
    entity_type: str                            # person | org | location | ...
    entity_id: int | None
    role: str | None
    raw_text: str


@dataclass
class EntityCorpus:
    documents: dict[str, DocumentInfo]
    nodes: dict[NodeId, NodeInfo]
    pages: dict[PageId, set[NodeId]] = field(default_factory=lambda: defaultdict(set))
    roles: dict[tuple[PageId, NodeId], set[str]] = field(default_factory=lambda: defaultdict(set))
    quotes: dict[tuple[PageId, NodeId], str] = field(default_factory=dict)

    @classmethod
    def build(cls, documents: list[DocumentInfo], nodes: list[NodeInfo], mentions: list[MentionRow]) -> EntityCorpus:
        corpus = cls(documents={d.doc_id: d for d in documents}, nodes={n.id: n for n in nodes})
        for m in mentions:
            if m.entity_type not in ("person", "org"):
                continue
            nid = f"{m.entity_type}:{m.entity_id}"
            if nid not in corpus.nodes:
                continue
            page = (m.doc_id, m.page)
            corpus.pages[page].add(nid)
            if m.role:
                corpus.roles[(page, nid)].add(m.role)
            corpus.quotes.setdefault((page, nid), " ".join(m.raw_text.split())[:160])
        return corpus

    def agency(self, doc_id: str) -> str:
        d = self.documents.get(doc_id)
        return d.agency if d else "?"

    def era(self, doc_id: str) -> str:
        d = self.documents.get(doc_id)
        return era(d.doc_date if d else None)


@dataclass(frozen=True)
class PageText:
    doc_id: str
    page: int
    text: str
