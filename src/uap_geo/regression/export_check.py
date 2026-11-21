"""Phase 4 gate, part 1: the PURSUE export, read through ``ExportTables``, gives the same tables as uap-geo's
own loaders on its pinned raw files. Run in CI with the regression caches restored; prints counts and
hashes only (the NUFORC rows are restricted).

Columns PURSUE does not carry are left out of the comparison and listed: NUFORC ``shape`` (unused
downstream) and ``country`` (PURSUE writes US tokens as "USA"; only the US-or-not test uses it).
"""

from __future__ import annotations

import hashlib
import logging

import pandas as pd

log = logging.getLogger(__name__)

SKIPPED = {"reports": ["shape", "country"]}


def _hash(frame: pd.DataFrame) -> str:
    return hashlib.sha256(pd.util.hash_pandas_object(frame, index=False).values.tobytes()).hexdigest()[:16]


def _compare(name: str, legacy: pd.DataFrame, export: pd.DataFrame, key: list[str], ordered: bool = False) -> dict:
    """Values equal after sorting by ``key``; with ``ordered``, also identical as given (order and dtypes)."""
    cols = [c for c in legacy.columns if c not in SKIPPED.get(name, []) and c != "geometry"]
    if ordered:
        try:
            pd.testing.assert_frame_equal(legacy[cols].reset_index(drop=True), export[cols].reset_index(drop=True))
            identical = True
        except AssertionError as e:
            identical = False
            first = str(e).strip().splitlines()[0] if str(e).strip() else "differs"
            out_note = first[:200]          # names the column and what differs; values follow on later lines
    a = legacy[cols].sort_values(key, kind="stable").reset_index(drop=True)
    b = export[cols].sort_values(key, kind="stable").reset_index(drop=True)
    out = {"rows": [len(a), len(b)], "skipped_columns": SKIPPED.get(name, [])}
    if len(a) != len(b):
        out["equal"] = False
        if name == "quakes":
            out["mag_below_3_or_missing"] = [int((~(legacy["mag"] >= 3)).sum()), int((~(export["mag"] >= 3)).sum())]
        return out
    diffs = {}
    for c in cols:
        x, y = a[c], b[c]
        if pd.api.types.is_float_dtype(x) or pd.api.types.is_float_dtype(y):
            same = ((x.astype(float) - y.astype(float)).abs() <= 1e-12) | (x.isna() & y.isna())
        else:
            same = (x.astype("string").fillna("<NA>") == y.astype("string").fillna("<NA>"))
        if not same.all():
            diffs[c] = int((~same).sum())
    out.update(equal=not diffs, differing_values=diffs, sha256=[_hash(a), _hash(b)])
    if ordered:
        out["identical_as_given"] = identical
        if not identical:
            out["first_difference"] = out_note
        out["equal"] = out["equal"] and identical
    return out


def check(config, root, tables) -> dict:
    """Compare every table the export replaces; ``tables`` is an ExportTables."""
    from uap_geo.common.download import Downloader
    from uap_geo.data.preprocessing.reports import ReportCleaner
    from uap_geo.data.scraping.gcat import GcatLaunchSource
    from uap_geo.data.scraping.kp import KpSource
    from uap_geo.data.scraping.registry import SourceRegistry
    from uap_geo.data.scraping.usgs import EarthquakeSource

    downloader = Downloader(config.paths.raw)
    sources = SourceRegistry(config, downloader)
    results = {}

    years = (2001, 2023)
    legacy, legacy_counts = ReportCleaner(*years).clean(sources.nuforc().load())
    export, export_counts = tables.reports(years)
    results["reports"] = _compare("reports", legacy, export, ["occurred_utc", "city", "summary"], ordered=True)
    results["reports"]["cleaning"] = [legacy_counts.__dict__, export_counts.__dict__]
    results["reports"]["equal"] &= legacy_counts == export_counts

    legacy = GcatLaunchSource(config.source("gcat_launches"), downloader, 100.0).load()
    results["launches"] = _compare("launches", legacy, tables.launches(100.0), ["tag"])
    starlink = GcatLaunchSource(config.source("gcat_launches"), downloader, 0.0).load()
    results["launches_any_apogee"] = _compare("launches", starlink, tables.launches(0.0), ["tag"])

    if (root / "data/raw/kp").exists():
        legacy_kp = KpSource(config.source("kp"), downloader).load()
        export_kp = tables.kp_daily()
        same = legacy_kp.index.equals(export_kp.index) and (legacy_kp.values == export_kp.values).all()
        results["kp_daily"] = {"rows": [len(legacy_kp), len(export_kp)], "equal": bool(same)}

    if (root / "data/raw/earthquakes").exists():
        q = EarthquakeSource(config.source("earthquakes"), downloader, 2001, 2026, 3.0).load()
        legacy_q = pd.DataFrame(q.drop(columns="geometry"))
        results["quakes"] = _compare("quakes", legacy_q, tables.quakes(2001, 2026, 3.0), ["time", "latitude", "longitude"])
    return results
