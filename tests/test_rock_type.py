import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import box

from uap_geo.features.rock_age import MISSING
from uap_geo.features.rock_type import CLASSES, CountyTypeSummary, UnitGrid, build_unit_grid, lith_class, unit_class_weights


def test_lith_class():
    assert lith_class("Unconsolidated", "Coarse-detrital") == "unconsolidated"
    assert lith_class("Sedimentary", "Carbonate") == "carbonate"
    assert lith_class("Sedimentary", "Chemical") == "clastic"
    assert lith_class("Igneous", "Hypabyssal") == "volcanic"
    assert lith_class("Igneous", "Plutonic") == "plutonic"
    assert lith_class("Metamorphic", "Metasedimentary") == "metasedimentary"
    assert lith_class("Metamorphic", "Gneiss") == "crystalline_metamorphic"
    assert lith_class("Tectonite", "Mylonite") == "crystalline_metamorphic"
    assert lith_class("Ice", None) is None


def test_unit_weights_split_major_lithologies_evenly():
    lith = pd.DataFrame({"UNIT_LINK": ["a", "a", "a", "b", "c"],
                         "LITH_RANK": ["Major", "Major", "Minor", "Indeterminate, major", "Major"],
                         "LITH1": ["Sedimentary", "Igneous", "Metamorphic", "Unconsolidated", "Ice"],
                         "LITH2": ["Carbonate", "Plutonic", "Gneiss", "Fine-detrital", None]})
    w = unit_class_weights(lith)
    assert list(w.columns) == list(CLASSES) and "c" not in w.index
    assert w.loc["a", "carbonate"] == 0.5 and w.loc["a", "plutonic"] == 0.5
    assert w.loc["a", "crystalline_metamorphic"] == 0      # minor lithology ignored
    assert w.loc["b", "unconsolidated"] == 1


def _grid():
    unit = np.array([[0, 0, 1, 1], [0, 2, 1, MISSING]], dtype=np.int32)
    county = np.array([[0, 0, 1, 1], [0, 0, 1, 1]], dtype=np.int32)
    return UnitGrid(unit, county, np.array(["u0", "u1", "ice"]), 0.0, 2.0, 1.0)


def test_county_shares_skip_unclassified_cells():
    w = pd.DataFrame(0.0, index=["u0", "u1"], columns=list(CLASSES))
    w.loc["u0", "carbonate"] = 1.0
    w.loc["u1", ["volcanic", "plutonic"]] = 0.5
    s = CountyTypeSummary(_grid(), w, np.array(["A", "B"]), np.array([1.0, 3.0]), np.array([1.0, 1.0]))
    out = s.summarize()
    assert out.loc["A", "type_cells"] == 3 and out.loc["A", "share_carbonate"] == 1.0   # 'ice' cell skipped
    assert out.loc["B", "type_cells"] == 3 and np.isclose(out.loc["B", "share_volcanic"], 0.5)
    assert out.loc["A", "dominant_type"] == "carbonate"


def test_shift_moves_units_and_marks_off_map_missing(tmp_path):
    g = _grid()
    moved = g.shifted(0.0, 1.0, 0.0, (0.0, 0.0))
    assert (moved[:, 0] == MISSING).all() and (moved[:, 1:] == g.unit[:, :3]).all()
    g.save(tmp_path / "u.npz")
    back = UnitGrid.load(tmp_path / "u.npz")
    assert (back.unit == g.unit).all() and list(back.units) == ["u0", "u1", "ice"]


def test_build_unit_grid():
    crs = "EPSG:5070"
    geology = gpd.GeoDataFrame({"unit_link": ["x", "y"]}, geometry=[box(0, 0, 2000, 2000), box(2000, 0, 4000, 2000)], crs=crs)
    counties = gpd.GeoDataFrame({"county_index": [0, 1]}, geometry=[box(0, 0, 2000, 2000), box(2000, 0, 4000, 2000)], crs=crs)
    g = build_unit_grid(geology, counties, 1000.0)
    assert list(g.units) == ["x", "y"]
    assert (g.unit[:, :2] == 0).all() and (g.unit[:, 2:] == 1).all()
