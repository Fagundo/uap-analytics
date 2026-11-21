"""A hash-only fingerprint of residual set v2: every report's tier and reasons, as uap-geo builds them.

PURSUE's per-record enrichment (refactor Phase 3b) must reproduce it on the same NUFORC extract and the same
GCAT files (the pinned-layer-inputs-v1 release); PURSUE's scripts/residual_parity.py uses the same canonical
form. Only hashes and counts are written: report text and record-level rows are restricted.

  report line:   report_id|tier|reasons          (reasons comma-joined in uap-geo's order)
  per reason:    SHA-256 of the sorted report ids carrying it, and their count
"""

from __future__ import annotations

import hashlib
from collections import Counter, defaultdict

import pandas as pd


def _digest(lines) -> str:
    return hashlib.sha256("\n".join(sorted(lines)).encode()).hexdigest()


def fingerprint(reports: pd.DataFrame) -> dict:
    lines = [f"{r.report_id}|{r.tier}|{r.reasons}" for r in reports.itertuples()]
    by_reason: dict[str, list[str]] = defaultdict(list)
    for r in reports.itertuples():
        for reason in filter(None, str(r.reasons).split(",")):
            by_reason[reason].append(r.report_id)
    return {
        "reports": len(reports),
        "sha256": _digest(lines),
        "report_ids": _digest(reports["report_id"]),
        "tiers": dict(sorted(Counter(reports["tier"]).items())),
        "tier_sha256": {t: _digest(reports.loc[reports["tier"] == t, "report_id"]) for t in sorted(reports["tier"].unique())},
        "reasons": {k: {"rows": len(v), "sha256": _digest(v)} for k, v in sorted(by_reason.items())},
    }
