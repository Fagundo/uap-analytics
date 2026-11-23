"""Run a replication on the pinned export, write its aggregates and summary, and check parity.

Outputs (committed; aggregates only, no record rows): results/replications/<name>/aggregates.json, report.md and,
with a reference, parity.md.
"""
from __future__ import annotations

import json
from pathlib import Path

from uap_geo.replications.inputs import ReplicationInputs
from uap_geo.replications.parity import ParityReport, compare, reduce
from uap_geo.replications.studies import REPLICATIONS

REFERENCE = Path("tests/parity/pursue_analytics_reference.json")


class ReplicationRunner:
    def __init__(self, root: Path, tables, export_tag: str):
        self.root, self.inputs, self.tag = root, ReplicationInputs(tables), export_tag

    def run(self, name: str) -> tuple[Path, ParityReport | None]:
        study = REPLICATIONS[name]()
        output = study.run(self.inputs)
        out = self.root / "results" / "replications" / name
        out.mkdir(parents=True, exist_ok=True)
        (out / "aggregates.json").write_text(json.dumps(reduce(name, output), indent=1, sort_keys=True) + "\n")
        (out / "report.md").write_text(Summary(name, study.title, self.tag).render(output) + "\n")
        parity = None
        ref_path = self.root / REFERENCE
        if ref_path.exists():
            parity = compare(name, json.loads(ref_path.read_text()), output)
            lines = [f"# Parity: {name}", "", f"Export {self.tag}; reference {REFERENCE}.", "",
                     f"Values checked: {parity.checked:,}; differences: {len(parity.differences):,}.", ""]
            lines += [f"- {d}" for d in parity.differences[:200]]
            if len(parity.differences) > 200:
                lines.append(f"- ... and {len(parity.differences) - 200:,} more")
            (out / "parity.md").write_text("\n".join(lines) + "\n")
        return out, parity


class Summary:
    """A short markdown report of a replication's output."""

    def __init__(self, name: str, title: str, tag: str):
        self.name, self.title, self.tag = name, title, tag

    def render(self, output: dict) -> str:
        head = [f"# Replication: {self.title}", "",
                f"Labelled replication of the data repository's `{self.name}` test, on the combined export {self.tag}. "
                "Method and settings unchanged; see parity.md for the number-for-number check against the original.", ""]
        return "\n".join(head + getattr(self, f"_{self.name}")(output))

    @staticmethod
    def _programs(output: dict) -> list[str]:
        lines = ["| Sighting set | n | Test | Coinciding | Chance | p |", "| --- | --- | --- | --- | --- | --- |"]
        for t in output["tests"]:
            test = "state" if t["method"] == "state" else f"{t['radius_km']:g} km"
            lines.append(f"| {t['dataset']} | {t['sightings']:,} | {test} | {t['observed']} | {t['null_mean']} | {t['p_value']} |")
        return lines

    @staticmethod
    def _nuclear(output: dict) -> list[str]:
        res = sorted(output["results"], key=lambda r: r["q_value"])
        lines = [f"{len(res)} tests over {len(output['sites'])} test sites; "
                 f"{sum(1 for r in res if r['q_value'] <= 0.1)} with q <= 0.10. Lowest q first:", "",
                 "| Catalog | Within | Tests | Days | Reports | Chance | p | q |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for r in res[:25]:
            near = f"{r['radius_km']:g} km" if r["radius_km"] else "anywhere"
            lines.append(f"| {r['dataset']} | {near} | {r['events']} | 0-{r['window_days']} | {r['observed']} | "
                         f"{r['null_mean']} | {r['p_value']} | {r['q_value']} |")
        return lines

    @staticmethod
    def _bluebook(output: dict) -> list[str]:
        cov = output["coverage"]
        lines = [f"Cases recovered: {sum(c['recovered'] for c in cov):,} of {sum(c['official'] for c in cov):,} "
                 "(Air Force totals).", "",
                 "| Program | Start | Conclusion | National before → after (p) | Region minus rest (p) |",
                 "| --- | --- | --- | --- | --- |"]
        for t in output["tests"]:
            nat = (f"{t['national_before']:.0%} → {t['national_after']:.0%} ({t['national_p']:.3f})"
                   if t["national_change"] is not None else "n/a")
            did = f"{t['did']:+.1%} ({t['did_p']:.3f})" if t["did"] is not None else "n/a"
            lines.append(f"| {t['program']} | {t['breakpoint']} | {t['label']} | {nat} | {did} |")
        return lines
