"""The network analyses as one JSON-ready report."""
from __future__ import annotations

from uap_geo.replications.networks.communities import CommunityResult
from uap_geo.replications.networks.corpus import EntityCorpus, NodeId
from uap_geo.replications.networks.routing import RoutingResult


class NetworkReport:
    def __init__(self, top: int = 25):
        self.top = top

    def build(self, corpus: EntityCorpus, routing: RoutingResult, communities: CommunityResult) -> dict:
        return {
            "routing": self._routing(corpus, routing),
            "communities": self._communities(corpus, communities),
        }

    @staticmethod
    def _node(corpus: EntityCorpus, nid: NodeId) -> dict:
        n = corpus.nodes[nid]
        aff = corpus.nodes.get(n.affiliation_org) if n.affiliation_org else None
        return {"id": nid, "kind": n.kind, "entity": n.entity_id, "name": n.name, "placeholder": n.placeholder,
                "affiliation": aff.name if aff else None}

    def _routing(self, corpus: EntityCorpus, r: RoutingResult) -> dict:
        def person_rows(counter, side):
            rows = []
            for nid, k in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[:self.top]:
                senders, recipients = r.correspondents(nid)
                mine = [x for x in r.letters if (x.addressee if side == "in" else x.author) == nid]
                rows.append({**self._node(corpus, nid), "letters": k,
                             "correspondents": len(senders if side == "in" else recipients),
                             "docs": sorted({x.doc_id for x in mine}),
                             "eras": sorted({corpus.era(x.doc_id) for x in mine})})
            return rows
        return {
            "letters_total": len(r.letters),
            "receivers": person_rows(r.received, "in"),
            "senders": person_rows(r.sent, "out"),
            "org_flows": [{"from": self._node(corpus, a), "to": self._node(corpus, b), "letters": k}
                          for (a, b), k in sorted(r.org_edges.items(), key=lambda kv: (-kv[1], kv[0]))[:self.top]],
            "letters": [{"doc": x.doc_id, "page": x.page, "author": self._node(corpus, x.author),
                         "addressee": self._node(corpus, x.addressee), "author_quote": x.author_quote,
                         "addressee_quote": x.addressee_quote, "era": corpus.era(x.doc_id)} for x in r.letters],
        }

    def _communities(self, corpus: EntityCorpus, c: CommunityResult) -> dict:
        return {
            "method": {"null_runs": c.null_runs, "alpha": c.alpha, "tested_pairs": c.tested_pairs,
                       "significant_ties": len(c.ties), "modularity": c.modularity, **c.stats},
            "communities": [{
                "id": k.id, "size": len(k.members), "internal_ties": k.internal_ties, "stability": k.stability,
                "agencies": k.agencies, "eras": k.eras, "cross_agency": k.cross_agency,
                "docs": [{"doc": d, "shared_pages": n} for d, n in k.docs.most_common()],
                "members": [{**self._node(corpus, m), "strength": k.strength[m]} for m in k.members],
                "evidence": [{"doc": d, "page": p} for d, p in k.evidence],
            } for k in c.communities],
            "ties": [{"a": self._node(corpus, t.a), "b": self._node(corpus, t.b), "pages": t.pages,
                      "null_mean": t.null_mean, "p": t.p_value, "docs": list(t.docs)} for t in c.ties],
        }
