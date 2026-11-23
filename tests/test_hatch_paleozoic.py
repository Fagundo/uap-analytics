import numpy as np
import pandas as pd
import pytest

from uap_geo.data.scraping.census_history import (
    mean_population,
    parse_cencounts,
    to_current_counties,
)


def test_cencounts_parser_carries_1990_counties_to_today():
    raw = pd.DataFrame({
        "fips": ["1000", "12025", "51083", "51780", "08013", "30113"],
        "name": ["Alabama", "Dade", "Halifax", "South Boston", "Boulder", "Yellowstone NP"],
        "pop1990": ["4040587", "1937094", "29033", "6997", "225339", "52"],
        "pop1980": ["3893888", "1625781", "30599", "7093", "189625", "275"],
        "pop1950": ["3061743", "495084", "41442", "", "48296", "0"]})
    long = to_current_counties(parse_cencounts(raw))
    assert "01000" not in set(long["geoid"])                              # state row dropped
    assert "12086" in set(long["geoid"]) and "12025" not in set(long["geoid"])
    assert "30113" not in set(long["geoid"])
    halifax = long.loc[(long["geoid"] == "51083") & (long["year"] == 1990), "population"].item()
    assert halifax == 29033 + 6997                                         # South Boston merged in
    m = mean_population(long, (1950, 1980, 1990)).set_index("geoid")
    assert m.loc["08013", "censuses"] == 3 and m.loc["08013", "population_hist"] == pytest.approx((48296 + 189625 + 225339) / 3)


def _rows():
    base = {"date_precision": "day", "lat": 40.0, "lon": -80.0, "coord_precision": "town", "country": "USA",
            "state": "PA", "flags": (), "strangeness": 6.0, "credibility": 7.0, "dedup_group": None,
            "explanation_tier": "residual"}
    rows = [
        {**base, "sighting_id": "hatch:1", "date": "1965-08-02"},
        {**base, "sighting_id": "hatch:2", "date": "1965-08-02", "dedup_group": "grp:a"},
        {**base, "sighting_id": "hatch:3", "date": "1965-08-02", "dedup_group": "grp:a"},       # same case
        {**base, "sighting_id": "hatch:4", "date": "1966-01-01", "flags": ("HOX",)},           # hoax
        {**base, "sighting_id": "hatch:5", "date": "1949-12-31"},                               # before
        {**base, "sighting_id": "hatch:6", "date": "1970-01-01", "state": "AK"},                # not CONUS
        {**base, "sighting_id": "hatch:7", "date": "1970-01-01", "country": "France", "state": None},
        {**base, "sighting_id": "hatch:8", "date": "1970-01-01", "lat": None},
        {**base, "sighting_id": "hatch:9", "date": "1971-01-01", "explanation_tier": "explained", "strangeness": 9.0},
    ]
    frame = pd.DataFrame(rows)
    frame["date"] = pd.to_datetime(frame["date"])
    return frame


def test_record_selection_and_tiers():
    pytest.importorskip("geopandas")
    from uap_geo.hypotheses.hatch_paleozoic import select_records

    records, steps = select_records(_rows(), (1950, 1999), 8)
    assert records["sighting_id"].tolist() == ["hatch:1", "hatch:2", "hatch:9"]
    assert steps["one per duplicate group"] == 3 and steps["not flagged as a hoax"] == 4
    assert records.set_index("sighting_id")["in_filtered"].to_dict() == {"hatch:1": True, "hatch:2": True, "hatch:9": False}
    assert records["in_high_strangeness"].tolist() == [False, False, True]


def test_spec_is_marked_post_hoc():
    from pathlib import Path

    import yaml
    root = Path(__file__).resolve().parents[1]
    spec = yaml.safe_load((root / "hypotheses" / "H-hatchpal-01.yaml").read_text())
    assert spec["splits"] == {"explore": [1950, 1959], "confirm": [1960, 1999]}
    assert spec["primary_tier"] == "filtered" and spec["status"].startswith("post hoc") and spec["registered"] is None


def test_combined_selection_and_panel():
    pytest.importorskip("geopandas")
    from uap_geo.hypotheses.diagnostics_combined import (
        CombinedPanelDiagnostics,
        one_per_group,
        select,
    )

    rows = _rows().assign(source="hatch")
    extra = rows.iloc[[0]].assign(sighting_id="nuforc:x", source="nuforc", flags=[("DUPLICATE",)], date=pd.Timestamp("2015-01-01"))
    keep = rows.iloc[[0]].assign(sighting_id="nicap:1", source="nicap", dedup_group="grp:a")
    r, _steps = select(pd.concat([rows, extra, keep], ignore_index=True))
    assert "nuforc:x" not in set(r["sighting_id"]) and "hatch:9" not in set(r["sighting_id"])   # repeat; explained
    combined = one_per_group(r)
    assert sorted(combined["sighting_id"]) == ["hatch:1", "hatch:2"]                         # grp:a kept once

    table = pd.DataFrame({"state_fips": ["42", "42"], "x": [1.0, 2.0]}, index=pd.Index(["42001", "42003"], name="geoid"))
    pop = pd.DataFrame({d: [100.0, 200.0] for d in range(1950, 2030, 10)}, index=table.index)
    recs = combined.assign(geoid="42001")
    panel = CombinedPanelDiagnostics(None)._panel(table, pop, recs)
    assert len(panel) == 16 and panel.loc[panel["decade"] == 1960, "report_count"].tolist() == [2, 0]
    assert panel["state_decade"].iloc[0] == "42_1950" and panel.index.is_unique and panel.index[0] == "42001_1950"


def test_stacked_dedup_stack_and_meta():
    pytest.importorskip("geopandas")
    from uap_geo.hypotheses import diagnostics_stacked as ds

    rows = pd.DataFrame({"sighting_id": ["hatch:1", "nicap:1", "nuforc:1", "nuforc:2"],
                         "source": ["hatch", "nicap", "nuforc", "nuforc"],
                         "dedup_group": ["g", "g", "h", None]})
    kept = ds.one_per_case(rows)
    assert sorted(kept["sighting_id"]) == ["nicap:1", "nuforc:1", "nuforc:2"]   # NICAP before Hatch

    table = pd.DataFrame({"state_fips": ["42", "42", "36"], "x": [0.1, 0.5, 0.9]},
                         index=pd.Index(["42001", "42003", "36001"], name="geoid"))
    pop = pd.DataFrame({d: [1e5, 2e5, 4e5] for d in range(1950, 2030, 10)}, index=table.index)
    rec = pd.DataFrame({"source": ["hatch"] * 150 + ["nuforc"] * 120 + ["nicap"] * 5,
                        "date": pd.to_datetime(["1955-06-01"] * 150 + ["2005-06-01"] * 120 + ["1955-06-01"] * 5),
                        "geoid": ["42001"] * 100 + ["36001"] * 50 + ["42003"] * 120 + ["42001"] * 5})
    ds.MIN_STRATUM = 100
    data = ds.stack(table, pop, rec, ["x"])
    assert set(data["stratum"]) == {"Hatch 1950s", "NUFORC 2000s"}               # NICAP 1950s too small
    assert data.groupby("stratum")["count"].sum().to_dict() == {"Hatch 1950s": 150, "NUFORC 2000s": 120}
    tot = (data["w_balanced"] / data["exposure"]).groupby(data["stratum"]).first() * data.groupby("stratum")["count"].sum()
    assert tot.round(6).nunique() == 1                                            # equal total vote per stratum
    assert data["cell"].iloc[0].startswith("Hatch_42_1950")

    m = ds.meta(pd.DataFrame({"log_rr": [0.1, 0.1, 0.1], "se": [0.05, 0.05, 0.05]}))
    assert m["I2"] == 0 and abs(m["random effects"]["rate_ratio"] - np.exp(0.1)) < 1e-12
