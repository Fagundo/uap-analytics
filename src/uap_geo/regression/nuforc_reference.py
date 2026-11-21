"""A hash-only fingerprint of the NUFORC reports exactly as uap-geo cleans them today.

PURSUE's NUFORC export must reproduce this fingerprint before uap-geo reads NUFORC from PURSUE (refactor
Phase 2). Only hashes and counts are written, so the file can be committed to a public repository.

Canonical form (PURSUE's scripts/nuforc_parity.py implements the same):
  rows  = contiguous-US reports after uap-geo's cleaning and duplicate removal, all years
  line  = report_id|occurred_utc|local_time|lat|lon|duration_s|state|city
          times as 'YYYY-MM-DD HH:MM:SS', lat/lon with 5 decimals, duration with 3, missing values empty
  lines sorted, joined with newlines, SHA-256; plus one digest per field over 'report_id|value' lines
"""

from __future__ import annotations

import hashlib
from collections import Counter

import pandas as pd

from uap_geo.classify.validation import report_ids
from uap_geo.data.preprocessing.reports import ReportCleaner
from uap_geo.events.timeutil import local_times

FIELDS = ("occurred_utc", "local_time", "lat", "lon", "duration_s", "state", "city")


def _fmt_time(v) -> str:
    return "" if pd.isna(v) else pd.Timestamp(v).strftime("%Y-%m-%d %H:%M:%S")


def _fmt_num(v, places: int) -> str:
    return "" if pd.isna(v) else f"{float(v):.{places}f}"


def canonical_rows(reports: pd.DataFrame) -> list[dict[str, str]]:
    rows = []
    for rid, r in zip(report_ids(reports), reports.itertuples(index=False)):
        rows.append({"report_id": rid, "occurred_utc": _fmt_time(r.occurred_utc), "local_time": _fmt_time(r.local_time),
                     "lat": _fmt_num(r.lat, 5), "lon": _fmt_num(r.lon, 5), "duration_s": _fmt_num(r.duration_s, 3),
                     "state": "" if pd.isna(r.state) else str(r.state), "city": "" if pd.isna(r.city) else str(r.city)})
    return rows


def fingerprint(rows: list[dict[str, str]]) -> dict:
    def digest(lines: list[str]) -> str:
        return hashlib.sha256("\n".join(sorted(lines)).encode()).hexdigest()

    out = {"rows": len(rows),
           "sha256": digest(["|".join([r["report_id"], *(r[f] for f in FIELDS)]) for r in rows]),
           "fields": {f: digest([f"{r['report_id']}|{r[f]}" for r in rows]) for f in FIELDS},
           "report_ids": digest([r["report_id"] for r in rows]),
           "rows_by_utc_year": dict(sorted(Counter(r["occurred_utc"][:4] for r in rows).items()))}
    return out


def reference(raw: pd.DataFrame) -> dict:
    reports, cleaning = ReportCleaner(1000, 3000).clean(raw)
    reports["local_time"] = local_times(reports)
    out = fingerprint(canonical_rows(reports))
    out["cleaning"] = cleaning.__dict__
    return out
