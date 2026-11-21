"""Licence-leak guard: no committed file may hold record-level restricted text (NUFORC summaries).

Checks every tracked Parquet and CSV file under results/ and data/ for text-bearing columns. Aggregates,
hashes and derived features (enums, probabilities) are fine."""
import re
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_COLUMNS = {"text", "summary", "description", "narrative"}


def _tracked(patterns):
    out = subprocess.run(["git", "ls-files", *patterns], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [ROOT / p for p in out.split()]


def _parquet_columns(path: Path) -> set[str]:
    data = path.read_bytes()
    n = struct.unpack("<I", data[-8:-4])[0]
    return {m.decode() for m in re.findall(rb"[A-Za-z_][A-Za-z0-9_]{1,40}", data[-8 - n:-8])}


def test_no_text_columns_in_committed_tables():
    offenders = []
    for path in _tracked(["results/**/*.parquet", "data/**/*.parquet", "results/*.parquet"]):
        if path.exists() and TEXT_COLUMNS & _parquet_columns(path):
            offenders.append(str(path.relative_to(ROOT)))
    for path in _tracked(["results/**/*.csv", "data/**/*.csv"]):
        if path.exists():
            header = path.read_text(errors="replace").split("\n", 1)[0].lower().split(",")
            if TEXT_COLUMNS & {h.strip().strip('"') for h in header}:
                offenders.append(str(path.relative_to(ROOT)))
    assert offenders == [], f"restricted text committed: {offenders}"
