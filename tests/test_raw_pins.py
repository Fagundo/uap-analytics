import json

import pytest

from uap_geo.regression.raw_pins import PinnedFile, RawPins


def _baseline(root, h, split, inputs):
    d = root / "results" / h / split
    d.mkdir(parents=True)
    (d / "regression_baseline.json").write_text(json.dumps({"result": {}, "fingerprint": {}, "inputs": inputs}))


def test_only_live_public_files_are_pinned(tmp_path):
    _baseline(tmp_path, "H-x", "explore", {"data/raw/airports/airports.csv": "a" * 64,
                                            "data/raw/counties/c.zip": "b" * 64,          # stable URL: not pinned
                                            "data/raw/nuforc/ufo_sightings.csv": "c" * 64})  # never pinned
    _baseline(tmp_path, "H-x", "confirm", {"data/raw/airports/airports.csv": "a" * 64,
                                            "data/raw/earthquakes/quakes_2026_m3.csv": "d" * 64})
    files = RawPins(tmp_path).files("H-x")
    assert [f.path for f in files] == ["data/raw/airports/airports.csv", "data/raw/earthquakes/quakes_2026_m3.csv"]
    assert files[0].asset == "aaaaaaaaaaaaaaaa-airports.csv"
    assert files[0].url.endswith("/releases/download/pinned-raw-inputs-v2/aaaaaaaaaaaaaaaa-airports.csv")


def test_splits_must_agree_on_a_files_copy(tmp_path):
    _baseline(tmp_path, "H-y", "explore", {"data/raw/airports/airports.csv": "a" * 64})
    _baseline(tmp_path, "H-y", "confirm", {"data/raw/airports/airports.csv": "e" * 64})
    with pytest.raises(ValueError):
        RawPins(tmp_path).files("H-y")


def test_seed_keeps_a_matching_file(tmp_path):
    import hashlib
    f = tmp_path / "data/raw/kp/Kp.txt"
    f.parent.mkdir(parents=True)
    f.write_text("kp")
    _baseline(tmp_path, "H-z", "explore", {"data/raw/kp/Kp.txt": hashlib.sha256(b"kp").hexdigest()})
    assert RawPins(tmp_path).seed("H-z") == {"data/raw/kp/Kp.txt": "kept"}
    assert PinnedFile("data/raw/kp/Kp.txt", "0" * 64).asset == "0000000000000000-Kp.txt"
