"""Command line entry point.

    uap-geo run --config configs/v1.yaml [--stage ingest build analyze]
    uap-geo run --start-year 2021 --end-year 2023 --tag holdout --shift-models R_confirmatory

`--tag` writes interim, processed and output files to a sub-folder, so a holdout run never overwrites
the main run. Raw downloads are shared.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from uap_geo.common.config import Config
from uap_geo.common.logging import configure


def _layer_counts(values: list[str]) -> dict[str, int]:
    out = {}
    for item in values:
        name, _, count = item.partition("=")
        out[name.strip()] = int(count)
    return out


def apply_overrides(config: Config, args: argparse.Namespace) -> Config:
    study = config.study
    changes = {}
    if args.permutations is not None:
        changes["shift_permutations"] = args.permutations
    if args.start_year is not None:
        changes["start_year"] = args.start_year
    if args.end_year is not None:
        changes["end_year"] = args.end_year
    if args.shift_models:
        changes["shift_models"] = tuple(args.shift_models)
    if args.layer_permutations:
        changes["shift_permutations_by_layer"] = {**study.shift_permutations_by_layer,
                                                  **_layer_counts(args.layer_permutations)}
    config = replace(config, study=replace(study, **changes))
    if args.tag:
        paths = config.paths
        config = replace(
            config,
            paths=replace(
                paths,
                interim=paths.interim / args.tag,
                processed=paths.processed / args.tag,
                outputs=paths.outputs / args.tag,
            ),
        )
    return config


def main(argv: list[str] | None = None) -> None:
    from uap_geo.pipeline import STAGES, V1Pipeline

    parser = argparse.ArgumentParser(prog="uap-geo")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="Run pipeline stages")
    run.add_argument("--config", type=Path, default=Path("configs/v1.yaml"))
    run.add_argument("--stage", nargs="+", choices=STAGES, default=list(STAGES))
    run.add_argument("--permutations", type=int, default=None, help="Override shift_permutations")
    run.add_argument("--start-year", type=int, default=None)
    run.add_argument("--end-year", type=int, default=None)
    run.add_argument("--tag", default=None, help="Sub-folder for interim/processed/outputs, e.g. 'holdout'")
    run.add_argument("--shift-models", nargs="*", default=None, help="Model names to shift-test")
    run.add_argument("--layer-permutations", nargs="*", default=None, help="Per-layer counts, e.g. rivers=1000")

    hyp = sub.add_parser("hypothesis", help="Pre-registered hypothesis tests")
    hyp.add_argument("action", choices=["run", "register", "diagnose"])
    hyp.add_argument("hypothesis_id")
    hyp.add_argument("--split", choices=["explore", "confirm", "holdout"], default="explore")
    hyp.add_argument("--config", type=Path, default=Path("configs/v1.yaml"))
    hyp.add_argument("--states", default=None, help="Comma-separated state FIPS codes for state diagnostics")
    hyp.add_argument("--diagnostic", default=None, help="Which diagnostic, for studies with several (e.g. land_use)")

    flt = sub.add_parser("filters", help="Explanation-filter validation")
    flt.add_argument("action", choices=["sample", "validate"])
    flt.add_argument("--per-rule", type=int, default=30)
    flt.add_argument("--random", type=int, default=100)
    flt.add_argument("--labels", type=Path, default=Path("configs/labels/filter_validation_v1.csv"))
    flt.add_argument("--config", type=Path, default=Path("configs/v1.yaml"))
    res = sub.add_parser("residual", help="Residual set: reports left after known explanations")
    res.add_argument("action", choices=["build"])
    res.add_argument("--settings", type=Path, default=Path("configs/residual.yaml"))
    res.add_argument("--config", type=Path, default=Path("configs/v1.yaml"))
    llm = sub.add_parser("llm", help="LLM feature extraction (needs ANTHROPIC_API_KEY)")
    llm.add_argument("action", choices=["sample", "extract", "validate", "submit", "collect", "gate", "describe"])
    llm.add_argument("--settings", type=Path, default=Path("configs/llm.yaml"))
    llm.add_argument("--per-group", type=int, default=40)
    llm.add_argument("--residual", type=int, default=120)
    llm.add_argument("--limit", type=int, default=None, help="extract: only the first N reports (smoke test)")
    llm.add_argument("--name", default="sample", help="file stem for sample/extract/validate outputs")
    llm.add_argument("--seed", type=int, default=7)
    llm.add_argument("--exclude", nargs="*", default=[], help="sample: names of earlier samples whose reports to leave out")
    aud = sub.add_parser("audit", help="Sensitivity checks on registered results")
    aud.add_argument("action", choices=["dispersion"])
    aud.add_argument("--split", choices=["explore", "confirm", "holdout"], default="confirm")
    aud.add_argument("--config", type=Path, default=Path("configs/v1.yaml"))
    reg = sub.add_parser("regression", help="Rerun committed hypothesis results and compare")
    reg.add_argument("action", choices=["run", "summarize", "nuforc-reference", "layers-reference"])
    reg.add_argument("--raw", type=Path, default=Path("data/raw"), help="layers-reference: folder of raw files")
    reg.add_argument("--only", default=None, help="One hypothesis id")
    reg.add_argument("--split", default=None)
    reg.add_argument("--record", action="store_true", help="Write missing input fingerprints when results match")
    reg.add_argument("--rebaseline", action="store_true",
                     help="Write regression baselines from this run (once; differences must be explained in BASELINE.md)")
    reg.add_argument("--out", type=Path, default=None, help="JSON file for this run's checks")
    reg.add_argument("--inputs", type=Path, default=Path("results/regression/parts"), help="summarize: folder of run JSONs")
    reg.add_argument("--config", type=Path, default=Path("configs/v1.yaml"))
    geo = sub.add_parser("geology", help="Inspect the geologic map inputs")
    geo.add_argument("action", choices=["terms"])
    geo.add_argument("--config", type=Path, default=Path("configs/v1.yaml"))
    args = parser.parse_args(argv)

    configure()
    if args.command == "run":
        config = apply_overrides(Config.from_yaml(args.config), args)
        V1Pipeline(config).run(tuple(args.stage))
    elif args.command == "hypothesis":
        _hypothesis(args)
    elif args.command == "filters":
        _filters(args)
    elif args.command == "residual":
        _residual(args)
    elif args.command == "llm":
        _llm(args)
    elif args.command == "geology":
        _geology_terms(args)
    elif args.command == "regression":
        _regression(args)
    elif args.command == "audit":
        from uap_geo.audit.dispersion import run as dispersion_run

        print(dispersion_run(Path.cwd(), Config.from_yaml(args.config), args.split).read_text())


def _regression(args) -> None:
    """Rerun committed results (run) or merge per-job outputs into one report (summarize). Exits 1 on any change."""
    import json
    import sys

    from uap_geo.regression.runner import RegressionRunner, summary_markdown

    if args.action == "nuforc-reference":
        from uap_geo.common.download import Downloader
        from uap_geo.data.scraping.registry import SourceRegistry
        from uap_geo.regression.nuforc_reference import reference

        config = Config.from_yaml(args.config)
        ref = reference(SourceRegistry(config, Downloader(config.paths.raw)).nuforc().load())
        out = args.out or Path("results/regression/nuforc_reference.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(ref, indent=1) + "\n")
        print(json.dumps({k: v for k, v in ref.items() if k != "fields"}, indent=1))
        return
    if args.action == "layers-reference":
        from uap_geo.regression.layers_reference import reference as layers_reference

        ref = layers_reference(args.raw)
        out = args.out or Path("results/regression/layers_reference.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(ref, indent=1) + "\n")
        print(json.dumps({k: (v if k != "quakes" else f"{len(v)} files") for k, v in ref.items()}, indent=1)[:4000])
        return
    if args.action == "run":
        runner = RegressionRunner(Path.cwd(), Config.from_yaml(args.config), STUDIES)
        targets = runner.targets(args.only, args.split)
        if not targets:
            raise SystemExit(f"No committed results for {args.only or 'any hypothesis'} {args.split or ''}")
        checks = [runner.check(h, s, record=args.record, rebaseline=args.rebaseline).as_dict() for h, s in targets]
        out = args.out or Path("results/regression/parts") / f"{args.only or 'all'}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(checks, indent=2) + "\n")
    else:
        checks = [c for f in sorted(args.inputs.glob("*.json")) for c in json.loads(f.read_text())]
        if not checks:
            raise SystemExit(f"No regression outputs in {args.inputs}")
    text = summary_markdown(checks)
    print(text)
    if args.action == "summarize":
        Path("results/regression").mkdir(parents=True, exist_ok=True)
        Path("results/regression/report.md").write_text(text)
    if not all(c["ok"] for c in checks):
        sys.exit(1)


def _geology_terms(args) -> None:
    """Counts of SGMC lithology terms, to fix the rock-type classes before any analysis."""
    from uap_geo.common.download import Downloader
    from uap_geo.data.scraping.registry import SourceRegistry

    config = Config.from_yaml(args.config)
    lith = SourceRegistry(config, Downloader(config.paths.raw)).geologic_map().lithology_table()
    print(f"Lithology rows: {len(lith):,}; units: {lith['UNIT_LINK'].nunique():,}; columns: {list(lith.columns)}")
    print(lith["LITH_RANK"].value_counts(dropna=False).to_string())
    major = lith.loc[lith["LITH_RANK"].astype(str).str.contains("ajor", na=False)]
    print(f"Units with a major lithology: {major['UNIT_LINK'].nunique():,}; major rows per unit (max): "
          f"{major.groupby('UNIT_LINK').size().max()}")
    for cols in (["LITH1"], ["LITH1", "LITH2"], ["LITH1", "LITH2", "LITH3"]):
        print(f"\n== major rows by {' / '.join(cols)}")
        print(major.groupby(cols, dropna=False).size().sort_values(ascending=False).head(60).to_string())


STUDIES = {"H-geo-01": "uap_geo.hypotheses.geo_triggers:GeoTriggerStudy",
           "H-launch-01": "uap_geo.hypotheses.launches:LaunchStudy",
           "H-celebrate-01": "uap_geo.hypotheses.celebrations:CelebrationStudy",
           "H-persist-01": "uap_geo.hypotheses.persistence:PersistenceStudy",
           "H-install-01": "uap_geo.hypotheses.proximity:InstallationStudy",
           "H-volcano-01": "uap_geo.hypotheses.proximity:VolcanoStudy",
           "H-rockage-01": "uap_geo.hypotheses.rock_age:RockAgeStudy",
           "H-rocktype-01": "uap_geo.hypotheses.rock_type:RockTypeStudy",
           "H-rockera-01": "uap_geo.hypotheses.rock_era:RockEraStudy"}
DIAGNOSTICS = {"H-geo-01": "uap_geo.hypotheses.diagnostics:DiagnosticsReport",
               "H-rockera-01": "uap_geo.hypotheses.diagnostics_era:StateEraDiagnostics",
               "H-rockera-01/land_use": "uap_geo.hypotheses.diagnostics_era:LandUseEraDiagnostics"}


def _hypothesis(args: argparse.Namespace) -> None:
    import importlib

    from uap_geo.hypotheses.spec import HypothesisRegistry

    root = Path.cwd()
    if args.action == "register":
        entry = HypothesisRegistry(root).register(args.hypothesis_id)
        print(f"Registered {args.hypothesis_id}: {entry}")
        return
    if args.hypothesis_id not in STUDIES:
        raise SystemExit(f"No study implemented for {args.hypothesis_id}; known: {sorted(STUDIES)}")
    module, cls = STUDIES[args.hypothesis_id].split(":")
    study = getattr(importlib.import_module(module), cls)(Config.from_yaml(args.config), root, args.split)
    if args.action == "diagnose":
        if args.hypothesis_id not in DIAGNOSTICS:
            raise SystemExit(f"No diagnostics for {args.hypothesis_id}")
        if args.states:
            study.diag_states = [x.strip().zfill(2) for x in args.states.split(",")]
        key = args.hypothesis_id if not args.diagnostic else f"{args.hypothesis_id}/{args.diagnostic}"
        if key not in DIAGNOSTICS:
            raise SystemExit(f"No diagnostic {key}")
        dmod, dcls = DIAGNOSTICS[key].split(":")
        path = getattr(importlib.import_module(dmod), dcls)(study).run()
    else:
        path = study.run()
    print(path.read_text())


def _filters(args: argparse.Namespace) -> None:
    from uap_geo.classify.validation import FilterSample, FilterValidation
    from uap_geo.data.scraping.kp import KpSource
    from uap_geo.hypotheses.geo_triggers import EventTable, GeoTriggerStudy

    root = Path.cwd()
    config = Config.from_yaml(args.config)
    study = GeoTriggerStudy(config, root, "explore")
    kp = KpSource(config.source("kp"), study.sources.downloader).load()
    table = EventTable(config, study.sources, study.filters, study.impl, study._all_years())
    tagged, labels, _, _ = table.labelled_reports(kp)
    sample = FilterSample(args.per_rule, args.random).draw(tagged, labels)
    out = root / "outputs" / "filter_sample.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(out, index=False)
    if args.action == "sample":
        print(f"FILTER SAMPLE ({len(sample)} reports)")
        for row in sample.itertuples():
            print(f"{row.report_id}\t{row.stratum}\t{row.rule if isinstance(row.rule, str) else '-'}\t{row.local_time:%Y-%m-%d %H:%M}\t"
                  f"{row.duration_s if row.duration_s == row.duration_s else ''}\t{row.summary}")
        return
    table_ = FilterValidation().precision(sample, root / args.labels)
    report = root / "results" / "filters" / "validation_v1.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Filter rule validation (v1)", "",
             "Labels written by Claude (an AI) on a stratified sample; not human-reviewed.", "",
             "| Rule | Labelled | Correct | Precision | Passes (>= 80%) |", "| --- | --- | --- | --- | --- |"]
    for rule, r in table_.iterrows():
        lines.append(f"| {rule} | {int(r['labelled'])} | {int(r['correct'])} | {r['precision']:.0%} | {'yes' if r['passes'] else 'no'} |")
    missed = table_.attrs.get("missed_in_random", {})
    lines += ["", f"Explainable reports the rules missed, in the random part of the sample: {missed or 'none'}."]
    report.write_text("\n".join(lines) + "\n")
    print(report.read_text())


def _residual(args: argparse.Namespace) -> None:
    from uap_geo.residual.builder import ResidualSetBuilder
    from uap_geo.residual.report import write_residual

    root = Path.cwd()
    result = ResidualSetBuilder(Config.from_yaml(args.config), root, root / args.settings).build()
    print(write_residual(result, root / "results" / "residual", args.settings.stem).read_text())


def _llm(args: argparse.Namespace) -> None:
    import json

    import pandas as pd
    import yaml

    from uap_geo.llm.extractor import FeatureExtractor
    from uap_geo.llm.strangeness import feature_table
    from uap_geo.llm.validation import stratified_sample, validation_report

    root = Path.cwd()
    s = yaml.safe_load((root / args.settings).read_text())
    out = root / s["out_dir"]
    out.mkdir(parents=True, exist_ok=True)
    residual = pd.read_parquet(root / s["residual_reports"])
    extractor = FeatureExtractor(s["model"], s["max_tokens"], schema=s.get("schema", "features-v1"))
    if args.action == "sample":
        exclude = set()
        for name in args.exclude:
            exclude |= set(pd.read_parquet(out / f"{name}_reports.parquet")["report_id"])
        sample = stratified_sample(residual, args.per_group, args.residual, args.seed, exclude)
        sample.to_parquet(out / f"{args.name}_reports.parquet", index=False)
        print(sample["group"].value_counts().to_string())
    elif args.action == "extract":
        rows = pd.read_parquet(out / f"{args.name}_reports.parquet")
        rows = rows.head(args.limit) if args.limit else rows
        raw = extractor.extract(rows[["report_id", "text", "duration_s"]])
        raw.to_parquet(out / f"{args.name}_features_raw.parquet", index=False)
        print(f"extracted {raw['features'].notna().sum()} of {len(raw)}; errors: {raw['error'].dropna().head(3).tolist()}")
    elif args.action == "validate":
        raw = pd.read_parquet(out / ("features_raw.parquet" if args.name == "full" else f"{args.name}_features_raw.parquet"))
        print(f"{raw['features'].notna().sum():,} of {len(raw):,} reports have features; errors: "
              f"{raw['error'].value_counts().to_dict()}")
        path = validation_report(feature_table(raw), residual, out / f"validation_{args.name}.md", args.name)
        print(path.read_text())
    elif args.action == "submit":
        rows = residual.loc[residual["text"].str.len() > 0, ["report_id", "text", "duration_s"]]
        ids = extractor.submit(rows)
        (out / "batches.json").write_text(json.dumps({"model": s["model"], "schema": extractor.schema, "batches": ids,
                                                      "requests": len(rows)}, indent=2))
        print(f"submitted {len(rows)} requests in {len(ids)} batches: {ids}")
    elif args.action == "gate":
        from uap_geo.common.download import Downloader
        from uap_geo.data.scraping.registry import SourceRegistry
        from uap_geo.llm.gate import KnownCauseGate

        cfg = Config.from_yaml(Path("configs/v1.yaml"))
        launches = SourceRegistry(cfg, Downloader(cfg.paths.raw)).launches(100.0).load()
        gate = KnownCauseGate(root, root / "configs" / "anomaly_gate_v2.yaml")
        table, passed = gate.run(launches)
        print(gate.report(table, passed, out / "gate_v2.md").read_text())
    elif args.action == "describe":
        from uap_geo.common.download import Downloader
        from uap_geo.data.scraping.registry import SourceRegistry
        from uap_geo.llm.gate import describe_twilight_launch_reports

        cfg = Config.from_yaml(Path("configs/v1.yaml"))
        launches = SourceRegistry(cfg, Downloader(cfg.paths.raw)).launches(100.0).load()
        text = describe_twilight_launch_reports(root, root / "configs" / "anomaly_gate_v2.yaml", launches)
        (out / "twilight_launch_reports.md").write_text(text + "\n")
        print(text)
    elif args.action == "collect":
        info = json.loads((out / "batches.json").read_text())
        status = extractor.status(info["batches"])
        print(status)
        if all(v == "ended" for v in status.values()):
            raw = extractor.collect(info["batches"])
            raw.to_parquet(out / "features_raw.parquet", index=False, compression="zstd")
            print(validation_report(feature_table(raw), residual, out / "validation_full.md", "full").read_text())


if __name__ == "__main__":
    main()
