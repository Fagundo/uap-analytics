"""NUFORC report cleaning counts and the state-code helper.

Since the data refactor (Phase 4) the reports come cleaned from PURSUE's export
(``data/scraping/pursue_export.py``), which reproduces the cleaning uap-geo used to do here (contiguous U.S.,
study years, later duplicates dropped) report for report; see results/regression/export_check.json.
"""

from __future__ import annotations

from dataclasses import dataclass

from uap_geo.common.geo import STATE_NAME_TO_CODE


def to_state_code(value: object) -> str | None:
    """'wa', 'WA', 'Washington' -> 'WA'; anything else is upper-cased as-is."""
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    return STATE_NAME_TO_CODE.get(text.lower(), text.upper())


@dataclass(frozen=True)
class CleaningReport:
    raw_rows: int
    undated: int
    outside_window: int
    outside_conus: int
    duplicates: int
    kept: int
