"""Check a replication's output against the original's aggregate reference, number for number.

The reference (tests/parity/pursue_analytics_reference.json) was written by the data repository's
``scripts/analytics_reference.py`` from the original commands' outputs: counts, null means, p-values, and a
SHA-256 of each sorted list of matching sighting ids (no text, no record rows). ``reduce`` turns a replication's
output into the same shape; ``compare`` lists every difference.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field


def ids_hash(ids: list[str]) -> str:
    return hashlib.sha256("\n".join(sorted(ids)).encode()).hexdigest()


def reduce(name: str, output: dict) -> object:
    if name == "programs":
        keep = ("dataset", "method", "radius_km", "sightings", "observed", "null_mean", "p_value")
        tests = [{**{k: t[k] for k in keep},
                  "per_program": {pid: {k: v for k, v in p.items() if k != "name"} for pid, p in t["per_program"].items()},
                  "matches": len(t["matches"]), "matches_sha256": ids_hash([m["id"] for m in t["matches"]])}
                 for t in output["tests"]]
        share = {n: {site: [[r["year"], r["all"], r["near"]] for r in rows] for site, rows in sites.items()}
                 for n, sites in output["local_share_by_year"].items()}
        return {"programs": tests, "local_share_by_year": share}
    if name == "nuclear":
        keep = ("site", "country", "kind", "dataset", "events", "sightings", "window_days", "radius_km",
                "covered_days", "covered_days_null", "observed", "null_mean", "p_value", "q_value")
        return {"nuclear": {"sites": output["sites"], "results": [{k: r[k] for k in keep} for r in output["results"]]}}
    if name == "bluebook":
        return {"bluebook": {k: output[k] for k in ("coverage", "by_year", "families", "tests")}}
    if name == "networks":
        return {"networks": _networks(output)}
    if name == "topics":
        return {"topics": _topics(output)}
    if name == "claims":
        return {"claims": _claims(output)}
    raise KeyError(name)


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _networks(report: dict) -> dict:
    r, c = report["routing"], report["communities"]
    people = lambda rows: [[x["id"], x["letters"], x["correspondents"], x["docs"]] for x in rows]  # noqa: E731
    letters = sorted(f"{x['doc']}|{x['page']}|{x['author']['id']}|{x['addressee']['id']}" for x in r["letters"])
    ties = sorted(f"{t['a']['id']}|{t['b']['id']}|{t['pages']}|{t['p']}|{t['null_mean']}" for t in c["ties"])
    return {"letters_total": r["letters_total"], "letters_sha256": digest(letters),
            "receivers": people(r["receivers"]), "senders": people(r["senders"]),
            "org_flows": [[f["from"]["id"], f["to"]["id"], f["letters"]] for f in r["org_flows"]],
            "method": c["method"], "ties": len(ties), "ties_sha256": digest(ties),
            "communities": [{"size": k["size"], "internal_ties": k["internal_ties"], "stability": k["stability"],
                             "agencies": k["agencies"], "eras": k["eras"],
                             "members": [m["id"] for m in k["members"]], "docs": [d["doc"] for d in k["docs"]]}
                            for k in c["communities"]]}


def _topics(report: dict) -> dict:
    def measure(m: dict) -> dict:
        return {"by_era": m["by_era"], "by_agency": m["by_agency"],
                "differences": [{k: d[k] for k in ("measure", "axis", "group", "docs", "group_value", "rest_value",
                                                   "lift", "p", "q", "lift_without_top", "robust")}
                                | {"drivers": [x["doc"] for x in d["drivers"]]} for d in m["differences"]]}
    return {"method": report["method"],
            "topics": [{"id": t["id"], "label": t["label"], "words": t["words"], "weights": t["weights"],
                        "typical": [[x["doc"], x["page"], x["share"]] for x in t["typical"]]} for t in report["topics"]],
            "topic_prevalence": measure(report["topic_prevalence"]),
            "themes": report["themes"], "theme_prevalence": measure(report["theme_prevalence"])}


def _claims(report: dict) -> dict:
    keep = ("claim", "case", "kind", "verdict", "metrics", "findings")
    return {"checks": [{k: x[k] for k in keep} for x in report["checks"]],
            "screen": [{k: x[k] for k in keep} for x in report["screen"]],
            "cases": [{"id": c["id"], "claims": c["claims"],
                       "pursue_incidents": sorted(i["incident"] for i in c.get("pursue_incidents", []))}
                      for c in report["cases"]]}


@dataclass
class ParityReport:
    name: str
    differences: list[str] = field(default_factory=list)
    checked: int = 0

    @property
    def ok(self) -> bool:
        return not self.differences


def _walk(path: str, ref, new, report: ParityReport, tol: float) -> None:
    if isinstance(ref, dict) and isinstance(new, dict):
        for k in sorted(set(ref) | set(new), key=str):
            if k not in new:
                report.differences.append(f"{path}/{k}: missing in the replication")
            elif k not in ref:
                report.differences.append(f"{path}/{k}: not in the reference")
            else:
                _walk(f"{path}/{k}", ref[k], new[k], report, tol)
        return
    if isinstance(ref, list) and isinstance(new, list):
        if len(ref) != len(new):
            report.differences.append(f"{path}: {len(ref)} items in the reference, {len(new)} in the replication")
        for i, (a, b) in enumerate(zip(ref, new)):
            _walk(f"{path}[{i}]", a, b, report, tol)
        return
    report.checked += 1
    if isinstance(ref, (int, float)) and isinstance(new, (int, float)) and not isinstance(ref, bool):
        if not math.isclose(ref, new, rel_tol=tol, abs_tol=tol):
            report.differences.append(f"{path}: reference {ref}, replication {new}")
    elif ref != new:
        report.differences.append(f"{path}: reference {ref!r}, replication {new!r}")


def keyed(section: list[dict], keys: tuple[str, ...]) -> dict:
    """List of results -> dict by identifying fields, so a missing or extra test shows by name, not position."""
    return {" | ".join(str(r.get(k)) for k in keys): r for r in section}


def compare(name: str, reference: dict, output: dict, tol: float = 1e-9) -> ParityReport:
    new = reduce(name, output)
    ref = {k: reference[k] for k in new}
    if name == "programs":
        ref = {**ref, "programs": keyed(ref["programs"], ("dataset", "method"))}
        new = {**new, "programs": keyed(new["programs"], ("dataset", "method"))}
    elif name == "nuclear":
        k = ("site", "kind", "dataset", "radius_km", "window_days")
        ref = {"nuclear": {**ref["nuclear"], "results": keyed(ref["nuclear"]["results"], k)}}
        new = {"nuclear": {**new["nuclear"], "results": keyed(new["nuclear"]["results"], k)}}
    elif name == "topics":
        # a topic's typical pages are the top shares; when several pages of one document tie (share 1.0), which
        # of them is listed can differ across numeric libraries, so typical pages compare as (document, share)
        def ties(t):
            return {**t, "topics": [{**x, "typical": sorted(([r[0], r[2]] for r in x["typical"]),
                                                            key=lambda r: (-r[1], r[0]))} for x in t["topics"]]}
        ref, new = {"topics": ties(ref["topics"])}, {"topics": ties(new["topics"])}
    elif name == "bluebook":
        k = ("program", "label")
        ref = {"bluebook": {**ref["bluebook"], "tests": keyed(ref["bluebook"]["tests"], k)}}
        new = {"bluebook": {**new["bluebook"], "tests": keyed(new["bluebook"]["tests"], k)}}
    report = ParityReport(name)
    _walk("", ref, new, report, tol)
    return report
