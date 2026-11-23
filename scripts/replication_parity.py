"""Run the replications on an unpacked export and compare them with a reference (Phase 6 parity).

The data repository's rebuild workflow runs this on the export it just built, against the reference it just
wrote from the original commands, so a change on either side shows before the export is published:

    PYTHONPATH=src python scripts/replication_parity.py --public EXPORT --restricted RESTRICTED \\
        --reference analytics_reference.json [--names programs nuclear bluebook]

Prints a summary (counts of values checked and differences, the first differences); exits 1 on any difference.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from uap_geo.data.scraping.pursue_export import ExportTables, LocalExport
from uap_geo.replications.inputs import ReplicationInputs
from uap_geo.replications.parity import compare
from uap_geo.replications.studies import REPLICATIONS


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--public", type=Path, required=True)
    ap.add_argument("--restricted", type=Path)
    ap.add_argument("--reference", type=Path, required=True)
    ap.add_argument("--names", nargs="+", default=list(REPLICATIONS))
    a = ap.parse_args()
    inputs = ReplicationInputs(ExportTables(LocalExport(a.public, a.restricted)))
    reference = json.loads(a.reference.read_text())
    failed = False
    for name in a.names:
        if name not in reference:                 # a reference from before this replication existed
            print(f"{name}: not in the reference, skipped")
            continue
        report = compare(name, reference, REPLICATIONS[name]().run(inputs))
        print(f"{name}: {report.checked:,} values checked, {len(report.differences):,} differences")
        for d in report.differences[:40]:
            print(f"  {d}")
        failed |= not report.ok
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
