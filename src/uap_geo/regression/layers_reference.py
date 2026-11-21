"""A hash-only fingerprint of the event layers exactly as uap-geo parses them from its pinned raw files.

PURSUE's context layers (refactor Phase 3) must reproduce it when they parse the same files; PURSUE's
scripts/layers_parity.py implements the same canonical form. The raw files themselves are public data
(GCAT CC-BY, GFZ Kp CC BY 4.0, USGS ComCat public domain) and are published as a release asset so PURSUE
can parse identical bytes.

Canonical lines (sorted, joined with newlines, SHA-256):
  launches  tag|time_utc|lat|lon|orbital|apogee_km|site   timed launches from contiguous-US sites, orbital
            or apogee >= 100 km; time 'YYYY-MM-DD HH:MM:SS', lat/lon 5 decimals, apogee 3, orbital true/false
  kp        start_utc|kp                                   3-hourly, 'YYYY-MM-DD HH:MM:SS', Kp 3 decimals
  quakes    per file: time|lat|lon|mag                     time with milliseconds, mag 2 decimals
"""

from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path

import pandas as pd

from uap_geo.data.scraping.gcat import parse_launches, parse_sites, us_space_launches
from uap_geo.data.scraping.kp import parse_kp_3hourly

KP_FILE = "kp/Kp_ap_since_1932.txt"
GCAT_FILES = ("gcat_launches/launch.tsv", "gcat_launches/sites.tsv")


def _digest(lines: list[str]) -> str:
    return hashlib.sha256("\n".join(sorted(lines)).encode()).hexdigest()


def _num(v, places: int) -> str:
    return "" if pd.isna(v) else f"{float(v):.{places}f}"


def _summary(lines: list[str], years: list[str]) -> dict:
    return {"rows": len(lines), "sha256": _digest(lines), "rows_by_year": dict(sorted(Counter(years).items()))}


def launch_lines(raw: Path) -> tuple[list[str], list[str]]:
    launches = parse_launches((raw / GCAT_FILES[0]).read_text(errors="replace"))
    sites = parse_sites((raw / GCAT_FILES[1]).read_text(errors="replace"))
    frame = us_space_launches(launches, sites, 100.0)
    lines = [f"{r.tag}|{r.time_utc:%Y-%m-%d %H:%M:%S}|{_num(r.lat, 5)}|{_num(r.lon, 5)}|{str(bool(r.orbital)).lower()}|"
             f"{_num(r.apogee_km, 3)}|{r.site}" for r in frame.itertuples()]
    return lines, [f"{t:%Y}" for t in frame["time_utc"]]


def kp_lines(raw: Path) -> tuple[list[str], list[str]]:
    kp = parse_kp_3hourly((raw / KP_FILE).read_text(errors="replace"))
    return ([f"{t:%Y-%m-%d %H:%M:%S}|{v:.3f}" for t, v in zip(kp["start_utc"], kp["kp"])],
            [f"{t:%Y}" for t in kp["start_utc"]])


def quake_lines(path: Path) -> list[str]:
    q = pd.read_csv(path, usecols=["time", "latitude", "longitude", "mag"])
    t = pd.to_datetime(q["time"], utc=True, format="ISO8601").dt.tz_localize(None)
    return [f"{ts.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}|{_num(la, 5)}|{_num(lo, 5)}|{_num(m, 2)}"
            for ts, la, lo, m in zip(t, q["latitude"], q["longitude"], q["mag"])]


def reference(raw: Path) -> dict:
    """Fingerprints of whatever layer files are present under data/raw, with each raw file's SHA-256."""
    out: dict = {"raw_files": {}}
    present = [f for f in (*GCAT_FILES, KP_FILE) if (raw / f).exists()]
    present += sorted(str(p.relative_to(raw)) for p in (raw / "earthquakes").glob("quakes_*.csv"))
    for f in present:
        out["raw_files"][f] = hashlib.sha256((raw / f).read_bytes()).hexdigest()
    if all((raw / f).exists() for f in GCAT_FILES):
        out["launches"] = _summary(*launch_lines(raw))
    if (raw / KP_FILE).exists():
        out["kp"] = _summary(*kp_lines(raw))
    quakes = {}
    for p in sorted((raw / "earthquakes").glob("quakes_*.csv")):
        lines = quake_lines(p)
        quakes[p.name] = {"rows": len(lines), "sha256": _digest(lines)}
    if quakes:
        out["quakes"] = quakes
    return out
