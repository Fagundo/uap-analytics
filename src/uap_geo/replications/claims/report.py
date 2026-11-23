"""Run every claim's check, and show where each case appears among the released files' incidents."""
from __future__ import annotations

from collections.abc import Iterable

from uap_geo.replications.claims.checks import check
from uap_geo.replications.claims.screen import SkyScreen
from uap_geo.replications.claims.model import Case, CheckResult, Claim
from uap_geo.replications.common.partial_dates import PartialDate


def find_incidents(case: Case, incidents: Iterable) -> list:
    """Incidents within a few days of the case whose location or summary names one of its place terms."""
    day = PartialDate.parse(case.start.date().isoformat())
    out = []
    for i in incidents:
        d = PartialDate.parse(i.date)
        if d is None or d.gap_days(day) > case.match_days:
            continue
        text = f"{i.location_text or ''} {i.summary or ''}".lower()
        if any(term in text for term in case.place_terms):
            out.append(i)
    return out


class ClaimReport:
    def build(self, cases: dict[str, Case], claims: list[Claim], incidents: list | None = None,
              screen: SkyScreen | None = None) -> dict:
        results: list[CheckResult] = [check(cases[k.case_id], k) for k in claims]
        screened = []
        if screen is not None:                    # every bright body above the horizon, for every case
            claimed = {(k.case_id, k.event.get("body")) for k in claims}
            for c in cases.values():
                for k in screen.claims_for(c):
                    if (c.id, k.event["body"]) not in claimed:
                        screened.append(check(c, k))
        case_rows = []
        for c in cases.values():
            row = {"id": c.id, "name": c.name, "start": c.start.isoformat(), "end": c.end.isoformat(),
                   "place": {"name": c.place.name, "lat": c.place.lat, "lon": c.place.lon, "note": c.place.note},
                   "observation_note": c.observation.note,
                   "claims": [r.claim.id for r in results if r.case.id == c.id], "sources": list(c.sources)}
            if incidents is not None:
                row["pursue_incidents"] = [{"incident": i.incident_id, "date": i.date, "location": i.location_text,
                                            "docs": i.doc_ids, "status": i.status, "verdicts": i.verdicts}
                                           for i in find_incidents(c, incidents)]
            case_rows.append(row)
        return {"cases": case_rows, "checks": [r.to_dict() for r in results],
                "screen": [r.to_dict() for r in screened]}
