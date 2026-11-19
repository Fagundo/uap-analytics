import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import box

from uap_geo.data.scraping.sgmc import unit_ages
from uap_geo.features.rock_age import MISSING, AgeGrid, CountyAgeSummary, build_age_grid, era_codes
from uap_geo.hypotheses.rock_age import two_sided_shift_p


def test_unit_ages_takes_widest_range_and_drops_undated():
    age = pd.DataFrame({"UNIT_LINK": ["a", "a", "b", "c"], "MIN_MA": [1.0, 2.0, None, 0.0],
                        "MAX_MA": [10.0, 30.0, 5.0, 0.0]})
    out = unit_ages(age).set_index("unit_link")
    assert list(out.index) == ["a"]
    assert out.loc["a", "min_ma"] == 1.0 and out.loc["a", "max_ma"] == 30.0
    assert np.isclose(out.loc["a", "log10_age"], np.log10(15.5))


def test_era_codes():
    assert era_codes(np.array([1.0, 100, 300, 1000, np.nan])).tolist() == [0, 1, 2, 3, MISSING]


def test_county_summary_and_centroid_fallback():
    la = np.log10(np.array([[1, 1, 100, 100], [1, 1, 1000, 1000.0]]))
    county = np.array([[0, 0, 1, 1], [0, 0, 1, MISSING]])
    g = AgeGrid(la, era_codes(10 ** la), county, 0.0, 2.0, 1.0)
    s = CountyAgeSummary(g, np.array(["a", "b", "c"]), np.array([0.5, 2.5, 3.5]), np.array([1.5, 1.5, 0.5]))
    out = s.summarize()
    assert np.isclose(out.loc["a", "rock_log10_age"], 0.0)
    assert np.isclose(out.loc["b", "rock_log10_age"], (2 + 2 + 3) / 3)
    assert np.isclose(out.loc["b", "share_mesozoic"], 2 / 3)
    assert out.loc["c", "rock_cells"] == 1 and out.loc["c", "dominant_era"] == "precambrian"


def test_shift_moves_map_and_marks_off_map_cells_missing():
    la = np.log10(np.array([[1, 10, 100, 1000.0]]))
    g = AgeGrid(la, era_codes(10 ** la), np.zeros((1, 4), int), 0.0, 1.0, 1.0)
    moved, era = g.shifted(0.0, 1.0, 0.0, (0.0, 0.0))
    assert np.isnan(moved[0, 0]) and era[0, 0] == MISSING
    assert np.allclose(moved[0, 1:], la[0, :3])
    same, _ = g.shifted(0.0, 0.0, 0.0, (2.0, 0.5))
    assert np.allclose(same, la)


def test_build_age_grid_rasterizes_units_and_counties():
    crs = "EPSG:5070"
    geology = gpd.GeoDataFrame({"log10_age": [0.0, 3.0]}, geometry=[box(0, 0, 2000, 2000), box(2000, 0, 4000, 2000)], crs=crs)
    counties = gpd.GeoDataFrame({"county_index": [0, 1]}, geometry=[box(0, 0, 2000, 2000), box(2000, 0, 4000, 2000)], crs=crs)
    g = build_age_grid(geology, counties, 1000.0)
    assert g.shape == (2, 4)
    assert np.allclose(g.log_age[:, :2], 0.0) and np.allclose(g.log_age[:, 2:], 3.0)
    assert (g.county[:, :2] == 0).all() and (g.county[:, 2:] == 1).all()
    assert (g.era[:, 2:] == 3).all()


def test_two_sided_shift_p():
    null = np.log(np.array([0.9, 1.0, 1.05, 1.2]))
    assert two_sided_shift_p(np.log(1.15), null) == (1 + 1) / 5
    assert two_sided_shift_p(np.log(1 / 1.15), null) == (1 + 1) / 5


def test_summary_survives_counties_with_no_dated_cells(tmp_path):
    la = np.array([[np.nan, np.nan, 2.0]])
    g = AgeGrid(la, era_codes(10 ** la), np.array([[0, 0, 1]]), 0.0, 1.0, 1.0)
    out = CountyAgeSummary(g, np.array(["a", "b"]), np.array([1.0, 2.5]), np.array([0.5, 0.5])).summarize()
    assert np.isnan(out.loc["a", "rock_log10_age"]) and pd.isna(out.loc["a", "dominant_era"])
    assert out.loc["b", "dominant_era"] == "mesozoic"
    g.save(tmp_path / "g.npz")
    back = AgeGrid.load(tmp_path / "g.npz")
    assert back.shape == g.shape and back.cell == 1.0 and (back.county == g.county).all()
