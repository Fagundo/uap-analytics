"""The one reader of PURSUE data (data refactor, Phase 4).

PURSUE publishes its combined export as a release of its private repository (``export-<version>``):
``export_public.tar.gz`` and ``export_restricted.tar.gz``. uap-geo pins one release in
configs/pursue_export.yaml (tag and SHA-256 of each asset), downloads it with a read-only token
(``PURSUE_EXPORT_TOKEN``), and turns it into the tables its code has always used:

* ``reports(years)``  NUFORC reports exactly as ``ReportCleaner(*years).clean`` returns them, with its
  cleaning counts, in the source file's order;
* ``launches(min_apogee_km)``  what ``GcatLaunchSource.load`` returns;
* ``kp_daily()``  what ``KpSource.load`` returns;
* ``quakes(first, last, min_mag)``  what ``EarthquakeSource.load`` returns (without geometry);
* ``explanations()``  PURSUE's residual-set flags per NUFORC report.

uap-geo never imports PURSUE's code: this module reads files that follow PURSUE's published JSON Schema.
The restricted tier is extracted under data/raw (gitignored) and never committed.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import tarfile
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import requests
import yaml

from uap_geo.common.geo import CONUS_STATES
from uap_geo.data.preprocessing.reports import CleaningReport

log = logging.getLogger(__name__)

ASSETS = ("export_public.tar.gz", "export_restricted.tar.gz")
API = "https://api.github.com"


@dataclass(frozen=True)
class ExportPin:
    repo: str
    tag: str
    sha256: dict[str, str]

    @classmethod
    def load(cls, path: Path) -> "ExportPin":
        d = yaml.safe_load(path.read_text())
        return cls(d["repo"], d["tag"], dict(d["sha256"]))


class PursueExport:
    def __init__(self, pin: ExportPin, cache: Path, token: str | None = None):
        self.pin = pin
        self.dir = cache / "pursue_export" / pin.tag
        self.token = token or os.environ.get("PURSUE_EXPORT_TOKEN") or os.environ.get("GH_TOKEN")

    # ------------------------------------------------------------------ download
    def _download(self, name: str) -> bytes:
        if not self.token:
            raise RuntimeError("PURSUE_EXPORT_TOKEN is not set: a read-only token for the private PURSUE repo is "
                               "needed to download its export (see docs/PURSUE_EXPORT.md)")
        headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json"}
        release = requests.get(f"{API}/repos/{self.pin.repo}/releases/tags/{self.pin.tag}", headers=headers, timeout=60)
        release.raise_for_status()
        asset = next((a for a in release.json()["assets"] if a["name"] == name), None)
        if asset is None:
            raise FileNotFoundError(f"{self.pin.repo} {self.pin.tag} has no asset {name}")
        resp = requests.get(asset["url"], headers={**headers, "Accept": "application/octet-stream"}, timeout=600)
        resp.raise_for_status()
        return resp.content

    def fetch(self) -> Path:
        for name, sub in zip(ASSETS, ("public", "restricted")):
            target = self.dir / sub
            if (target / ".sha256").exists() and (target / ".sha256").read_text().strip() == self.pin.sha256[name]:
                continue
            data = self._download(name)
            digest = hashlib.sha256(data).hexdigest()
            if digest != self.pin.sha256[name]:
                raise ValueError(f"{name}: SHA-256 {digest} differs from the pinned {self.pin.sha256[name]}")
            target.mkdir(parents=True, exist_ok=True)
            archive = self.dir / name
            archive.write_bytes(data)
            with tarfile.open(archive) as tar:
                tar.extractall(target, filter="data")
            archive.unlink()
            (target / ".sha256").write_text(digest + "\n")
            log.info("PURSUE export %s: %s extracted to %s", self.pin.tag, name, target)
        return self.dir

    # ------------------------------------------------------------------ files
    def manifest(self) -> dict:
        return json.loads((self.fetch() / "public" / "manifest.json").read_text())

    def table(self, relative: str, restricted: bool = False) -> pd.DataFrame:
        path = self.fetch() / ("restricted" if restricted else "public") / relative
        return pd.read_csv(path, dtype=str, keep_default_na=False)

    def nuforc_rows(self) -> pd.DataFrame:
        rows = self.table("sightings_restricted.csv", restricted=True)
        rows = rows.loc[rows["source"] == "nuforc"].copy()
        rows["source_order"] = rows["source_order"].astype(int)
        return rows.sort_values("source_order").reset_index(drop=True)


def _num(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.replace("", pd.NA), errors="coerce")


def _utc(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series.replace("", pd.NA), utc=True, format="ISO8601").dt.tz_localize(None)


def _na(series: pd.Series) -> pd.Series:
    return series.replace("", pd.NA).astype("string")


class ExportTables:
    """The export as the tables uap-geo's code consumes (see the module docstring)."""

    def __init__(self, export: PursueExport):
        self.export = export

    def reports(self, years: tuple[int, int]) -> tuple[pd.DataFrame, CleaningReport]:
        rows = self.export.nuforc_rows()
        frame = pd.DataFrame({
            # In this extract the reported time is the UTC time for every row; PURSUE keeps the UTC one.
            "occurred": pd.to_datetime(rows["occurred_utc"].replace("", pd.NA), utc=True, format="ISO8601"),
            "city": _na(rows["place_text"]),
            "state": rows["state"].replace("", None).astype("str"),     # dtype as ReportCleaner's state map
            "country": _na(rows["country"]),
            "summary": _na(rows["text"]),
            "shape": pd.Series(pd.NA, index=rows.index, dtype="string"),
            "occurred_utc": _utc(rows["occurred_utc"]),
            "duration_s": _num(rows["duration_s"]).astype(float),
            "timezone": _na(rows["timezone"]),
            "lat": _num(rows["lat"]).astype(float),
            "lon": _num(rows["lon"]).astype(float),
        })
        flags = rows["flags"].map(lambda f: set(json.loads(f or "[]")))
        n_raw = len(frame)
        dated = frame["occurred"].notna()
        window = dated & frame["occurred"].dt.year.between(*years)
        us = frame["country"].isna() | (frame["country"] == "USA")       # PURSUE writes US tokens as "USA"
        conus = window & us & frame["state"].isin(CONUS_STATES) & frame["city"].notna()
        kept = conus & ~flags.map(lambda f: "DUPLICATE" in f)
        report = CleaningReport(raw_rows=n_raw, undated=int((~dated).sum()), outside_window=int((dated & ~window).sum()),
                                outside_conus=int((window & ~conus).sum()), duplicates=int((conus & ~kept).sum()),
                                kept=int(kept.sum()))
        return frame.loc[kept].reset_index(drop=True), report

    def launches(self, min_apogee_km: float = 100.0) -> pd.DataFrame:
        rows = self.export.table("layers/launches.csv")
        attrs = rows["attributes"].map(json.loads)
        out = pd.DataFrame({
            "tag": rows["item_id"].str.removeprefix("gcat:"),
            "time_utc": _utc(rows["start_utc"]),
            "timed": attrs.map(lambda a: a["timed"] == "true"),
            "vehicle": attrs.map(lambda a: a["vehicle"] or pd.NA),
            "site": attrs.map(lambda a: a["site"]),
            "apogee_km": pd.to_numeric(attrs.map(lambda a: a["apogee_km"] or None), errors="coerce"),
            "launch_code": attrs.map(lambda a: a["launch_code"]),
            "mission": attrs.map(lambda a: a["mission"]),
            "orbital": attrs.map(lambda a: a["orbital"] == "true"),
            "lat": _num(rows["lat"]).astype(float),
            "lon": _num(rows["lon"]).astype(float),
            "name": attrs.map(lambda a: a["site_name"] or pd.NA),
        })
        space = out["orbital"] | (out["apogee_km"] >= min_apogee_km)
        return out.loc[space & out["timed"]].sort_values(["time_utc", "tag"], kind="stable").reset_index(drop=True)

    def kp_daily(self) -> pd.Series:
        rows = self.export.table("layers/kp.csv")
        kp = pd.DataFrame({"start_utc": _utc(rows["start_utc"]),
                           "kp": rows["attributes"].map(lambda a: float(json.loads(a)["kp"]))})
        return kp.groupby(kp["start_utc"].dt.normalize())["kp"].max().rename("kp_max").rename_axis("date_utc")

    def quakes(self, first_year: int, last_year: int, min_magnitude: float) -> pd.DataFrame:
        rows = self.export.table("layers/quakes.csv")
        attrs = rows["attributes"].map(json.loads)
        out = pd.DataFrame({"time": _utc(rows["start_utc"]), "latitude": _num(rows["lat"]).astype(float),
                            "longitude": _num(rows["lon"]).astype(float),
                            "mag": pd.to_numeric(attrs.map(lambda a: a["mag"] or None), errors="coerce")})
        years = out["time"].dt.year.between(first_year, last_year)
        return out.loc[years & (out["mag"] >= min_magnitude)].sort_values("time", kind="stable").reset_index(drop=True)

    def explanations(self) -> pd.DataFrame:
        rows = self.export.nuforc_rows()
        return pd.DataFrame({"report_id": rows["sighting_id"].str.split(":").str[1],
                             "explanations": rows["explanations"].map(lambda e: json.loads(e or "[]")),
                             "tier": _na(rows["explanation_tier"])})
