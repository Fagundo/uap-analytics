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
    added: list[str] = field(default_factory=list)
    inputs_changed: list[str] = field(default_factory=list)
    against: str = "registered result"      # or "baseline"
    error: str | None = None
    seconds: float = 0.0

    @property
    def ok(self) -> bool:
        # A changed raw file is reported but is not a failure on its own: the values are what must not move.
        return self.error is None and not self.differences and self.fingerprint in ("match", "recorded")

    def as_dict(self) -> dict:
        return {"hypothesis": self.hypothesis, "split": self.split, "ok": self.ok, "error": self.error,
                "seconds": round(self.seconds, 1), "fingerprint": self.fingerprint,
                "against": self.against, "added": self.added[:20], "n_added": len(self.added),
                "inputs_changed": self.inputs_changed,
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

    def check(self, hypothesis: str, split: str, record: bool = False, rebaseline: bool = False) -> RunCheck:
        """Rerun one committed result and compare it with its regression baseline when one exists (the
        documented starting point of the refactor), otherwise with the registered result itself.

        record: write the input fingerprint when the comparison is clean. rebaseline: write the baseline
        (result, fingerprint and input-file hashes) from this run, whatever the comparison found; used once,
        with every difference from the registered result explained in results/regression/BASELINE.md."""
        result = RunCheck(hypothesis, split)
        start = time.time()
        out_dir = self.root / "results" / hypothesis / split
        try:
            module, cls = self.studies[hypothesis].split(":")
            study = getattr(importlib.import_module(module), cls)(self.config, self.root, split)
            table, _, manifest, card = study.evaluate()
            actual = json.loads(json.dumps(card.as_dict(), default=float))
            prints = InputFingerprint.of(table)
            baseline_path = out_dir / "regression_baseline.json"
            if baseline_path.exists() and not rebaseline:
                baseline = json.loads(baseline_path.read_text())
                expected, result.against = baseline["result"], "baseline"
                stored_prints = baseline["fingerprint"]
                result.inputs_changed = sorted(k for k, v in baseline["inputs"].items()
                                               if manifest.inputs.get(k, v) != v)
            else:
                expected = json.loads((out_dir / "results.json").read_text())
                fp_path = out_dir / "fingerprint.json"
                stored_prints = json.loads(fp_path.read_text()) if fp_path.exists() else None
            result.differences = self.comparer.compare(expected, actual)
            result.added = self.comparer.added(expected, actual)
            if stored_prints is not None:
                result.fingerprint_differences = self.comparer.compare(stored_prints, prints)
                result.fingerprint = "differs" if result.fingerprint_differences else "match"
            elif record and not result.differences:
                (out_dir / "fingerprint.json").write_text(json.dumps(prints, indent=2) + "\n")
                result.fingerprint = "recorded"
            if rebaseline:
                used = {k: v for k, v in manifest.inputs.items() if k.startswith("data/raw/")}
                baseline_path.write_text(json.dumps({"result": actual, "fingerprint": prints, "inputs": used},
                                                    indent=1, default=float) + "\n")
                result.fingerprint = "recorded"
        except Exception as exc:  # noqa: BLE001 - one failing study must not hide the others
            log.exception("Regression check failed for %s %s", hypothesis, split)
            result.error = f"{type(exc).__name__}: {exc}"
        result.seconds = time.time() - start
        return result


def summary_markdown(checks: list[dict]) -> str:
    lines = ["# Regression check", "", "Each committed result rerun from the current code and data and compared "
             "value by value (relative tolerance 1e-5; run metadata ignored). A raw file that differs from the one the "
             "baseline used is listed as a warning; the split still passes when every value matches.", "",
             "| Hypothesis | Split | Compared with | Result | Values differing | New fields | Inputs | Raw files changed | Minutes |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for c in checks:
        status = "error" if c["error"] else (("same, raw differs" if c.get("inputs_changed") else "same")
                                             if c["ok"] else "CHANGED")
        lines.append(f"| {c['hypothesis']} | {c['split']} | {c.get('against', 'registered result')} | {status} | "
                     f"{c['n_differences']} | {c.get('n_added', 0)} | {c['fingerprint']} | "
                     f"{len(c.get('inputs_changed', []))} | {c['seconds'] / 60:.1f} |")
    for c in checks:
        if c["error"] or c["differences"] or c["fingerprint_differences"] or c.get("inputs_changed"):
            lines += ["", f"## {c['hypothesis']} {c['split']}", ""]
            if c["error"]:
                lines.append(f"Error: {c['error']}")
            lines += [f"- raw input changed: {f}" for f in c.get("inputs_changed", [])]
            lines += [f"- {d}" for d in c["differences"] + c["fingerprint_differences"]]
    return "\n".join(lines) + "\n"
