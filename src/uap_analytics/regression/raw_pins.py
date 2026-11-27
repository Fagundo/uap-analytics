"""Pinned copies of the live raw inputs, so regression reruns read exactly the files their baselines used.

Some sources change under the same URL (OurAirports daily, USGS earthquake files for recent years, GCAT launch
lists, Kp, the Smithsonian volcano list, Census estimate vintages). Actions caches held the baseline's copies
but expire, after which a rerun downloads newer files and its numbers drift. Instead, every live file a baseline
used is stored once as an asset of the release ``pinned-raw-inputs-v2``, named by its SHA-256, and each rerun
seeds ``data/raw`` from those assets before it starts. The baseline already records each file's SHA-256 (its
``inputs``), so no separate lock file is needed.

Only public, redistributable sources are pinned (public domain or CC BY, cited in the release notes). Sighting
data (NUFORC, the data repository's export) is never pinned here; the export has its own versioned release.
"""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path

import requests

log = logging.getLogger(__name__)

REPO = "Fagundo/uap-analytics"
TAG = "pinned-raw-inputs-v2"
LIVE = ("data/raw/airports/", "data/raw/earthquakes/", "data/raw/gcat_launches/", "data/raw/kp/",
        "data/raw/volcanoes/", "data/raw/population/", "data/raw/place_population/")
NEVER = ("data/raw/nuforc/", "data/raw/pursue_export/")
NOTES = ("Copies of the live raw files the regression baselines used, one asset per file content, named <first 16 hex "
         "of SHA-256>-<file name>. Regression reruns seed data/raw from here (uap-analytics regression seed --only H), so a "
         "changed upstream file cannot move a result.\n\nSources and licences: OurAirports airports.csv (public "
         "domain); USGS earthquake catalog (public domain); GCAT launch and site lists, Jonathan McDowell (CC BY 4.0); "
         "Kp index, GFZ Potsdam (CC BY 4.0); Global Volcanism Program, Volcanoes of the World, Smithsonian "
         "Institution (Holocene list, cited); U.S. Census Bureau population estimates (public domain). No sighting "
         "data is stored here.")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


@dataclass(frozen=True)
class PinnedFile:
    path: str                                     # e.g. data/raw/airports/airports.csv
    sha256: str

    @property
    def asset(self) -> str:
        return f"{self.sha256[:16]}-{Path(self.path).name}"

    @property
    def url(self) -> str:
        return f"https://github.com/{REPO}/releases/download/{TAG}/{self.asset}"


class RawPins:
    def __init__(self, root: Path):
        self.root = root

    def files(self, hypothesis: str) -> list[PinnedFile]:
        """Live raw files the hypothesis's regression baselines used (one entry per path and content)."""
        found: dict[tuple[str, str], PinnedFile] = {}
        for base in sorted((self.root / "results" / hypothesis).glob("*/regression_baseline.json")):
            for path, digest in json.loads(base.read_text())["inputs"].items():
                if path.startswith(LIVE) and not path.startswith(NEVER):
                    found[(path, digest)] = PinnedFile(path, digest)
        paths = [f.path for f in found.values()]
        if len(paths) != len(set(paths)):
            raise ValueError(f"{hypothesis}: splits' baselines used different copies of the same raw file")
        return sorted(found.values(), key=lambda f: f.path)

    def seed(self, hypothesis: str) -> dict[str, str]:
        """Put the pinned copy of every live file in place. Returns path -> 'kept' | 'seeded' | 'missing'."""
        out = {}
        for f in self.files(hypothesis):
            target = self.root / f.path
            if target.exists() and sha256(target) == f.sha256:
                out[f.path] = "kept"
                continue
            resp = requests.get(f.url, timeout=300)
            if resp.status_code == 404:
                log.warning("%s: no pinned copy (%s); the run will download a fresh one", f.path, f.asset)
                out[f.path] = "missing"
                continue
            resp.raise_for_status()
            if hashlib.sha256(resp.content).hexdigest() != f.sha256:
                raise ValueError(f"{f.asset}: content does not match its SHA-256")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(resp.content)
            out[f.path] = "seeded"
        return out

    def record(self, hypothesis: str) -> dict[str, str]:
        """Upload the live files the (new) baselines used, unless the release already has them (needs gh and
        GH_TOKEN). Returns path -> 'uploaded' | 'present'."""
        self._ensure_release()
        present = set(subprocess.run(["gh", "release", "view", TAG, "-R", REPO, "--json", "assets", "-q",
                                      ".assets[].name"], capture_output=True, text=True, check=True).stdout.split())
        out = {}
        for f in self.files(hypothesis):
            if f.asset in present:
                out[f.path] = "present"
                continue
            local = self.root / f.path
            if sha256(local) != f.sha256:
                raise ValueError(f"{f.path}: local file differs from the baseline's; record right after a rebaseline")
            staged = local.with_name(f.asset)
            staged.write_bytes(local.read_bytes())
            done = subprocess.run(["gh", "release", "upload", TAG, str(staged), "-R", REPO],
                                  capture_output=True, text=True)
            staged.unlink()
            if done.returncode != 0 and "already_exists" not in done.stderr:   # another job uploaded it first
                raise RuntimeError(done.stderr)
            out[f.path] = "uploaded"
        return out

    @staticmethod
    def _ensure_release() -> None:
        view = ["gh", "release", "view", TAG, "-R", REPO]
        if subprocess.run(view, capture_output=True).returncode == 0:
            return
        made = subprocess.run(["gh", "release", "create", TAG, "-R", REPO, "--title", "Pinned live raw inputs (regression)",
                               "--notes", NOTES], capture_output=True, text=True)
        if made.returncode != 0 and subprocess.run(view, capture_output=True).returncode != 0:   # not a race: fail
            raise RuntimeError(made.stderr)
