"""Loading the case catalog (the export's datasets/case_claims.json)."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from uap_analytics.replications.claims.model import Case, Claim, Observation, Place


def _time(value: str) -> datetime:
    t = datetime.fromisoformat(value)
    if t.tzinfo is None:
        raise ValueError(f"case time without a timezone: {value!r}")
    return t


def load_catalog(path: Path) -> tuple[dict[str, Case], list[Claim]]:
    return parse_catalog(json.loads(path.read_text()))


def parse_catalog(raw: dict) -> tuple[dict[str, Case], list[Claim]]:
    cases = {}
    for c in raw["cases"]:
        start = _time(c["start"])
        cases[c["id"]] = Case(
            id=c["id"], name=c["name"], start=start, end=_time(c["end"]) if c.get("end") else start,
            place=Place(**c["place"]), observation=Observation(**c.get("observation", {})),
            place_terms=tuple(c.get("place_terms", [])),
            match_days=c.get("match_days", 5),
            sources=tuple(c.get("sources", [])))
    claims = []
    for k in raw["claims"]:
        if k["case"] not in cases:
            raise KeyError(f"claim {k['id']} names unknown case {k['case']}")
        claims.append(Claim(id=k["id"], case_id=k["case"], kind=k["kind"], explanation=k["explanation"],
                            claimed_by=k["claimed_by"], event=k["event"], sources=tuple(k.get("sources", [])),
                            disputes=tuple(k.get("disputes", []))))
    return cases, claims
