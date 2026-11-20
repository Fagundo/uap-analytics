"""USGS State Geologic Map Compilation (SGMC; Horton, San Juan and Stoeser 2017, doi:10.5066/F7WH2N65).

48 state geologic maps (1:50,000 to 1:1,000,000) in one geodatabase. Each map-unit polygon links (UNIT_LINK)
to the Age table, which gives the unit's age range in millions of years (MIN_MA youngest, MAX_MA oldest).
Units are not reconciled across state borders, so analyses compare counties within states.
"""

from __future__ import annotations

import logging
import zipfile

import geopandas as gpd
import numpy as np
import pandas as pd

from uap_geo.common.base import DataSource

log = logging.getLogger(__name__)
GEOLOGY_LAYER = "SGMC_Geology"
AGE_LAYER = "Age"
LITH_LAYER = "Lithology"
FILENAME = "USGS_SGMC_Geodatabase.zip"


def unit_ages(age: pd.DataFrame) -> pd.DataFrame:
    """One row per UNIT_LINK: youngest (min_ma) and oldest (max_ma) bound, their midpoint and log10 midpoint.

    A unit listed more than once keeps its widest range. Units with no usable age (water, ice,
    unmapped) are dropped and later count as missing."""
    a = pd.DataFrame({"unit_link": age["UNIT_LINK"].astype(str),
                      "min_ma": pd.to_numeric(age["MIN_MA"], errors="coerce"),
                      "max_ma": pd.to_numeric(age["MAX_MA"], errors="coerce")})
    a = a.dropna(subset=["min_ma", "max_ma"])
    a = a.loc[(a["max_ma"] > 0) & (a["min_ma"] >= 0) & (a["max_ma"] >= a["min_ma"])]
    out = a.groupby("unit_link").agg(min_ma=("min_ma", "min"), max_ma=("max_ma", "max"))
    out["mid_ma"] = (out["min_ma"] + out["max_ma"]) / 2
    out["log10_age"] = np.log10(out["mid_ma"])
    return out.reset_index()


def gdb_path(zip_path) -> str:
    """GDAL path to the file geodatabase inside the downloaded zip (read in place, never extracted)."""
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
    gdbs = sorted({n[: n.index(".gdb") + 4] for n in names if ".gdb/" in n})
    if not gdbs:
        raise FileNotFoundError(f"No .gdb inside {zip_path}")
    return f"/vsizip/{zip_path}/{gdbs[0]}"


class SgmcGeologySource(DataSource):
    """Map-unit polygons with their age range, in the map's own CRS (reprojected by the caller)."""

    def load(self) -> gpd.GeoDataFrame:
        import pyogrio

        # Map rings are already oriented (outer clockwise, holes counter-clockwise); trusting that avoids
        # GDAL's slow full polygon reassembly (30 minutes for this layer).
        pyogrio.set_gdal_config_options({"OGR_ORGANIZE_POLYGONS": "ONLY_CCW"})

        path = self.downloader.fetch(self.config, FILENAME)  # mirrors tried in order
        gdb = gdb_path(path)
        log.info("SGMC layers: %s", [name for name, _ in pyogrio.list_layers(gdb)])
        age = pyogrio.read_dataframe(gdb, layer=AGE_LAYER, read_geometry=False, columns=["UNIT_LINK", "MIN_MA", "MAX_MA"])
        ages = unit_ages(age)
        units = pyogrio.read_dataframe(gdb, layer=GEOLOGY_LAYER, columns=["UNIT_LINK"])
        units = units.rename(columns={"UNIT_LINK": "unit_link"})
        units["unit_link"] = units["unit_link"].astype(str)
        out = units.merge(ages, on="unit_link", how="left")
        dated = out["log10_age"].notna()
        log.info("SGMC: %d polygons, %d units with an age, %.1f%% of polygons dated", len(out), len(ages),
                 100 * dated.mean())
        return gpd.GeoDataFrame(out, geometry="geometry", crs=units.crs)

    def lithology_table(self):
        """The Lithology table (one row per unit and lithology term), without geometry: fast to read."""
        import pyogrio

        path = self.downloader.fetch(self.config, FILENAME)
        return pyogrio.read_dataframe(gdb_path(path), layer=LITH_LAYER, read_geometry=False)

    def age_table(self):
        """The Age table (UNIT_LINK, MIN_MA, MAX_MA), without geometry."""
        import pyogrio

        path = self.downloader.fetch(self.config, FILENAME)
        return pyogrio.read_dataframe(gdb_path(path), layer=AGE_LAYER, read_geometry=False,
                                      columns=["UNIT_LINK", "MIN_MA", "MAX_MA"])
