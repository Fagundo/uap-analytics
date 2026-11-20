"""Rerun every committed hypothesis result and compare it with what is in the repository."""

from __future__ import annotations

import importlib
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

from uap_geo.common.config import Config
from uap_geo.regression.compare import Difference, ResultComparer
from uap_geo.regression.fingerprint import InputFingerprint

log = logging.getLogger(__name__)


@dataclass
class RunCheck:
    hypothesis: str
    split: str
    differences: list[Difference] = field(default_factory=list)
    fingerprint: str = "missing"          # match | differs | recorded | missing
    fingerprint_differences: list[Difference] = field(default_factory=list)
    error: str | None = None
    seconds: float = 0.0

    @property
    def ok(self) -> bool:
        return self.error is None and not self.differences and self.fingerprint in ("match", "recorded")

    def as_dict(self) -> dict:
        return {"hypothesis": self.hypothesis, "split": self.split, "ok": self.ok, "error": self.error,
                "seconds": round(self.seconds, 1), "fingerprint": self.fingerprint,
                "differences": [d.line() for d in self.differences[:50]], "n_differences": len(self.differences),
                "fingerprint_differences": [d.line() for d in self.fingerprint_differences]}


class RegressionRunner:
    def __init__(self, root: Path, config: Config, studies: dict[str, str], comparer: ResultComparer | None = None) -> None:
        self.root = root
        self.config = config
        self.studies = studies
        self.comparer = comparer or ResultComparer()

    def targets(self, only: str | None = None, split: str | None = None) -> list[tuple[str, str]]:
        """Every (hypothesis, split) with a committed results.json, for hypotheses the CLI knows."""
        found = []
        for path in sorted((self.root / "results").glob("H-*/*/results.json")):
            hyp, sp = path.parent.parent.name, path.parent.name
            if hyp in self.studies and (only is None or hyp == only) and (split is None or sp == split):
                found.append((hyp, sp))
        return found

    def check(self, hypothesis: str, split: str, record: bool = False) -> RunCheck:
        result = RunCheck(hypothesis, split)
        start = time.time()
        out_dir = self.root / "results" / hypothesis / split
        try:
            module, cls = self.studies[hypothesis].split(":")
            study = getattr(importlib.import_module(module), cls)(self.config, self.root, split)
            table, _, _, card = study.evaluate()
            expected = json.loads((out_dir / "results.json").read_text())
            actual = json.loads(json.dumps(card.as_dict(), default=float))
            result.differences = self.comparer.compare(expected, actual)
            prints = InputFingerprint.of(table)
            fp_path = out_dir / "fingerprint.json"
            if fp_path.exists():
                stored = json.loads(fp_path.read_text())
                result.fingerprint_differences = self.comparer.compare(stored, prints)
                result.fingerprint = "differs" if result.fingerprint_differences else "match"
            elif record and not result.differences:
                fp_path.write_text(json.dumps(prints, indent=2) + "\n")
                result.fingerprint = "recorded"
        except Exception as exc:  # noqa: BLE001 - one failing study must not hide the others
            log.exception("Regression check failed for %s %s", hypothesis, split)
            result.error = f"{type(exc).__name__}: {exc}"
        result.seconds = time.time() - start
        return result


def summary_markdown(checks: list[dict]) -> str:
    lines = ["# Regression check", "", "Each committed result rerun from the current code and data and compared "
             "value by value (relative tolerance 1e-6; run metadata ignored).", "",
             "| Hypothesis | Split | Result | Values differing | Inputs | Minutes |", "| --- | --- | --- | --- | --- | --- |"]
    for c in checks:
        status = "error" if c["error"] else ("same" if c["ok"] else "CHANGED")
        lines.append(f"| {c['hypothesis']} | {c['split']} | {status} | {c['n_differences']} | {c['fingerprint']} | "
                     f"{c['seconds'] / 60:.1f} |")
    for c in checks:
        if c["error"] or c["differences"] or c["fingerprint_differences"]:
            lines += ["", f"## {c['hypothesis']} {c['split']}", ""]
            if c["error"]:
                lines.append(f"Error: {c['error']}")
            lines += [f"- {d}" for d in c["differences"] + c["fingerprint_differences"]]
    return "\n".join(lines) + "\n"
