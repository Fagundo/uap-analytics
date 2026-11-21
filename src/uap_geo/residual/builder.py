"""Builds the residual set: every report and event labelled explained / possible / residual, with the
reason, and the report text with NUFORC notes stripped (the input to blinded LLM extraction).

The labels are PURSUE's explanation flags (its export, rules and checks as in configs/residual_v2.yaml);
uap-geo keeps uap-geo's reason format: the first high-confidence rule, then every matching check."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml

from uap_geo.classify.validation import report_ids
from uap_geo.common.config import Config
from uap_geo.common.download import Downloader
from uap_geo.data.scraping.registry import SourceRegistry
from uap_geo.hypotheses.event_table import EventTable
from uap_geo.residual.checks import strip_notes

log = logging.getLogger(__name__)
EVENT_PARAMS = {"dedup": {"km": 50, "hours": 3}, "quality": {"min_reports": 2, "min_duration_s": 300}}


@dataclass
class ResidualResult:
    reports: pd.DataFrame
    events: pd.DataFrame
    summary: dict


class ResidualSetBuilder:
    def __init__(self, config: Config, root: Path, settings_path: Path) -> None:
        self.config = config
        self.root = root
        self.settings = yaml.safe_load(settings_path.read_text())
        self.filters = yaml.safe_load((root / self.settings["rule_filters"]).read_text())
        self.sources = SourceRegistry(config, Downloader(config.paths.raw))

    @staticmethod
    def reasons(explanations: list[str]) -> list[str]:
        """uap-geo's reasons from PURSUE's labels: the first high rule (config order), then the checks."""
        rules = [e.split(":")[1] for e in explanations if e.startswith("rule:") and e.endswith(":high")]
        return rules[:1] + [e.split(":")[1] for e in explanations if e.startswith("check:")]

    def _llm_features(self, params: dict) -> pd.DataFrame:
        from uap_geo.llm.strangeness import feature_table

        raw = pd.read_parquet(self.root / params["features"])
        table = feature_table(raw)
        self.llm_table = table
        log.info("LLM features: %d reports (%s)", len(table), table.attrs.get("schema", "?"))
        return table

    def build(self) -> ResidualResult:
        years = tuple(self.settings["years"])
        table = EventTable(self.config, self.sources, self.filters, EVENT_PARAMS_IMPL, years)
        tagged, labels, events, _ = table.labelled_reports(None)
        reports = tagged.copy()
        reports["report_id"] = report_ids(reports)
        reports["text"] = strip_notes(reports["summary"]).str.lower()
        flags = self.sources.export_tables().explanations().set_index("report_id")
        missing = ~reports["report_id"].isin(flags.index)
        if missing.any():
            raise ValueError(f"{int(missing.sum())} reports have no explanation flags in the PURSUE export")
        labels_ = reports["report_id"].map(flags["explanations"])
        reasons = labels_.map(self.reasons)
        reports["tier"] = reports["report_id"].map(flags["tier"]).astype(str)
        counts: dict[str, int] = {}
        for explanations in labels_:
            high_rules = [e.split(":")[1] for e in explanations if e.startswith("rule:") and e.endswith(":high")]
            keys = [f"rule:{r}" for r in high_rules[:1]] + [e.split(":")[1] for e in explanations if e.startswith("check:")]
            for key in keys:
                counts[key] = counts.get(key, 0) + 1
        if "llm_explainer" in self.settings["checks"]:
            self._llm_features(self.settings["checks"]["llm_explainer"])
        llm = getattr(self, "llm_table", None)
        if llm is not None and len(llm):
            flags = llm.set_index("report_id")
            reports["strangeness"] = reports["report_id"].map(flags["strangeness"])
            reports["high_strangeness"] = reports["report_id"].map(flags["high_strangeness"])
            reports["llm_top_cause"] = reports["report_id"].map(flags["top_conventional"])
        reports["reasons"] = reasons.map(lambda r: ",".join(r))

        rank = {"explained": 2, "possible": 1, "residual": 0}
        ev_rank = reports.assign(r=reports["tier"].map(rank)).groupby("event_id")["r"].max()
        inverse = {v: k for k, v in rank.items()}
        events = events.assign(tier=events["event_id"].map(ev_rank).map(inverse))
        summary = {
            "years": list(years), "reports": len(reports), "events": len(events),
            "report_tiers": reports["tier"].value_counts().to_dict(),
            "event_tiers": events["tier"].value_counts().to_dict(),
            "matches": counts,
        }
        log.info("Residual set: %s", summary)
        keep = ["report_id", "event_id", "occurred_utc", "local_time", "lat", "lon", "city", "state", "duration_s",
                "text", "tier", "reasons", "strangeness", "high_strangeness", "llm_top_cause"]
        return ResidualResult(reports[[c for c in keep if c in reports.columns]], events, summary)


# EventTable reads dedup and quality settings from an implementation block.
EVENT_PARAMS_IMPL = {"parameters": EVENT_PARAMS}
