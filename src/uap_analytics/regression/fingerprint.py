"""Fingerprints of what a study analysed: which reports and events, in which counties and on which nights.

Stored next to each committed result (fingerprint.json). When the data pipeline moves to uap-data, matching
fingerprints show the studies still see exactly the same inputs."""

from __future__ import annotations

import hashlib

import pandas as pd

from uap_analytics.common.geo import COUNTY_ID

EVENT_COLUMNS = ("event_id", COUNTY_ID, "night", "in_filtered", "in_high_quality")


def _digest(frame: pd.DataFrame) -> str:
    text = frame.astype(str).to_csv(index=False, lineterminator="\n")
    return hashlib.sha256(text.encode()).hexdigest()


class InputFingerprint:
    @staticmethod
    def of(table) -> dict:
        out: dict = {}
        reports = getattr(table, "reports", None)
        if isinstance(reports, pd.DataFrame):
            from uap_analytics.classify.validation import report_ids

            ids = pd.DataFrame({"report_id": sorted(report_ids(reports).astype(str))})
            out["reports"] = {"count": len(ids), "sha256": _digest(ids)}
        events = getattr(table, "events", None)
        if isinstance(events, pd.DataFrame):
            cols = [c for c in EVENT_COLUMNS if c in events.columns]
            ev = events[cols].copy()
            if "night" in ev:
                ev["night"] = pd.to_datetime(ev["night"]).dt.strftime("%Y-%m-%d")
            ev = ev.sort_values(cols).reset_index(drop=True)
            out["events"] = {"count": len(ev), "columns": cols, "sha256": _digest(ev)}
            if COUNTY_ID in ev:
                per_county = ev.groupby(COUNTY_ID).size().rename("events").reset_index().sort_values(COUNTY_ID)
                out["county_counts"] = {"counties": len(per_county), "sha256": _digest(per_county)}
        return out
