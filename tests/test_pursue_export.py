"""ExportTables on a tiny synthetic export, the registry switch, and the import boundary."""
import csv
import json
import re
from pathlib import Path

import pandas as pd
import pytest

from uap_geo.data.scraping.pursue_export import ExportPin, ExportTables, PursueExport

ROOT = Path(__file__).resolve().parents[1]
SIGHTING_COLS = ["sighting_id", "source", "tier", "occurred_utc", "date_start", "time_local", "lat", "lon", "state",
                 "country", "place_text", "duration_s", "timezone", "source_order", "text", "flags", "explanations",
                 "explanation_tier"]
LAYER_COLS = ["layer", "item_id", "start_utc", "end_utc", "lat", "lon", "label", "attributes"]


def _write(path: Path, cols, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def _sighting(i, utc, state="AZ", country="USA", city="Phoenix", flags="[]", order=0, **kw):
    return {"sighting_id": f"nuforc:{i}", "source": "nuforc", "tier": "restricted", "occurred_utc": utc,
            "lat": "33.4484", "lon": "-112.074", "state": state, "country": country, "place_text": city,
            "duration_s": "60.0", "timezone": "America/Phoenix", "source_order": str(order), "text": f"light {i}",
            "flags": flags, "explanations": '["check:holiday_night:possible"]', "explanation_tier": "possible", **kw}


@pytest.fixture
def tables(tmp_path):
    root = tmp_path / "export"
    _write(root / "restricted" / "sightings_restricted.csv", SIGHTING_COLS, [
        _sighting("b", "2010-07-05T04:00:00+00:00", order=1),
        _sighting("a", "2010-07-05T03:00:00+00:00", order=0),
        _sighting("c", "2010-07-05T04:10:00+00:00", order=2, flags='["DUPLICATE"]'),
        _sighting("d", "1999-01-01T00:00:00+00:00", order=3),                       # outside the window
        _sighting("e", "2010-01-01T00:00:00+00:00", order=4, state="AK"),           # outside CONUS
        _sighting("f", "2010-01-01T00:00:00+00:00", order=5, country="CA"),         # not US
        {**_sighting("g", "2010-01-01T00:00:00+00:00", order=6), "source": "hatch"},
    ])
    _write(root / "public" / "layers" / "kp.csv", LAYER_COLS, [
        {"layer": "kp", "item_id": "kp:2003-10-29T00:00", "start_utc": "2003-10-29T00:00:00Z", "attributes": '{"kp": "9.0"}'},
        {"layer": "kp", "item_id": "kp:2003-10-29T03:00", "start_utc": "2003-10-29T03:00:00Z", "attributes": '{"kp": "8.667"}'}])
    launch = {"site": "V", "site_name": "Vandenberg", "vehicle": "Falcon 9", "launch_code": "OS", "orbital": "true",
              "apogee_km": "", "timed": "true", "mission": "Starlink 1"}
    _write(root / "public" / "layers" / "launches.csv", LAYER_COLS, [
        {"layer": "launches", "item_id": "gcat:2020-001", "start_utc": "2020-01-07T02:19:00Z", "lat": "34.6",
         "lon": "-120.6", "attributes": json.dumps(launch)},
        {"layer": "launches", "item_id": "gcat:2020-S01", "start_utc": "2020-01-08T02:19:00Z", "lat": "34.6",
         "lon": "-120.6", "attributes": json.dumps({**launch, "launch_code": "SU", "orbital": "false", "apogee_km": "50.0"})}])
    _write(root / "public" / "layers" / "quakes.csv", LAYER_COLS, [
        {"layer": "quakes", "item_id": "comcat:x", "start_utc": "2011-08-23T17:51:04.020Z", "lat": "37.9", "lon": "-77.9",
         "attributes": '{"mag": "5.8"}'},
        {"layer": "quakes", "item_id": "comcat:y", "start_utc": "2011-08-24T00:00:00.000Z", "lat": "37.9", "lon": "-77.9",
         "attributes": '{"mag": "2.9"}'}])

    class Local(PursueExport):
        def fetch(self):
            return root

    return ExportTables(Local(ExportPin("Fagundo/PURSUE", "export-test", {}), tmp_path))


def test_reports_like_report_cleaner(tables):
    frame, report = tables.reports((2001, 2023))
    assert list(frame.columns) == ["occurred", "city", "state", "country", "summary", "shape", "occurred_utc",
                                   "duration_s", "timezone", "lat", "lon"]
    assert frame["summary"].tolist() == ["light a", "light b"]                   # source order, duplicate dropped
    assert str(frame["occurred"].dt.tz) == "UTC" and frame["occurred_utc"].dt.tz is None
    assert report.__dict__ == {"raw_rows": 6, "undated": 0, "outside_window": 1, "outside_conus": 2,
                               "duplicates": 1, "kept": 2}


def test_layers(tables):
    kp = tables.kp_daily()
    assert kp.name == "kp_max" and kp.iloc[0] == 9.0
    assert tables.launches(100.0)["tag"].tolist() == ["2020-001"]
    assert tables.launches(0.0)["tag"].tolist() == ["2020-001", "2020-S01"]
    assert tables.quakes(2001, 2026, 3.0)["mag"].tolist() == [5.8, 2.9]      # all the M3 query returned
    assert tables.quakes(2001, 2026, 4.0)["mag"].tolist() == [5.8]


def test_explanations(tables):
    e = tables.explanations()
    assert set(e["report_id"]) == {"a", "b", "c", "d", "e", "f"} and set(e["tier"]) == {"possible"}


def test_registry_reads_the_pinned_export(monkeypatch, tmp_path):
    pytest.importorskip("geopandas")
    from uap_geo.common.config import Config
    from uap_geo.common.download import Downloader
    from uap_geo.data.scraping import registry as reg

    config = Config.from_yaml(ROOT / "configs" / "v1.yaml")
    pin = tmp_path / "pin.yaml"
    pin.write_text("repo: Fagundo/PURSUE\ntag: export-test\nsha256: {}\n")
    monkeypatch.setattr(reg, "EXPORT_PIN", pin)
    tables = reg.SourceRegistry(config, Downloader(tmp_path)).export_tables()
    assert isinstance(tables, ExportTables) and tables.export.pin.tag == "export-test"
    assert ExportPin.load(ROOT / "configs" / "pursue_export.yaml").tag.startswith("export-")


def test_import_boundary():
    """uap-geo reads PURSUE's export files; it never imports the PURSUE package."""
    offenders = [str(p.relative_to(ROOT)) for p in (ROOT / "src").rglob("*.py")
                 if re.search(r"^\s*(import pursue\b|from pursue\b)", p.read_text(), re.MULTILINE)]
    assert offenders == []
