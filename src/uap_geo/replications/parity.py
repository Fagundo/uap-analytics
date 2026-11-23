"""Check a replication's output against the original's aggregate reference, number for number.

The reference (tests/parity/pursue_analytics_reference.json) was written by the data repository's
``scripts/analytics_reference.py`` from the original commands' outputs: counts, null means, p-values, and a
SHA-256 of each sorted list of matching sighting ids (no text, no record rows). ``reduce`` turns a replication's
output into the same shape; ``compare`` lists every difference.
"""
from __future__ import annotations

import hashlib
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
    raise KeyError(name)


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
    elif name == "bluebook":
        k = ("program", "label")
        ref = {"bluebook": {**ref["bluebook"], "tests": keyed(ref["bluebook"]["tests"], k)}}
        new = {"bluebook": {**new["bluebook"], "tests": keyed(new["bluebook"]["tests"], k)}}
    report = ParityReport(name)
    _walk("", ref, new, report, tol)
    return report
