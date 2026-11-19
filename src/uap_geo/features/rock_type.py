"""County shares of surface rock type (lithology), from the USGS State Geologic Map Compilation.

Each map unit lists one or more major lithologies (Lithology table, LITH_RANK 'Major' or 'Indeterminate,
major'), coded LITH1 > LITH2 > ... A unit's weight in each rock-type class is the fraction of its major
lithologies in that class. The map is rasterized once as unit indices; a county's class shares average the
weights over its cells, and the layer-shift test moves the unit raster, so every class shifts together.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from uap_geo.features.rock_age import MISSING, RasterGrid

# Rock-type classes, fixed from the SGMC term counts (uap-geo geology terms) before any analysis.
CLASSES: tuple[str, ...] = ("unconsolidated", "clastic", "carbonate", "volcanic", "plutonic",
                            "metasedimentary", "crystalline_metamorphic")
CLASS_LABELS = {
    "unconsolidated": "Unconsolidated sediment (sand, gravel, clay, silt, glacial and alluvial deposits)",
    "clastic": "Clastic and other sedimentary rock (sandstone, shale, mudstone, conglomerate, chert, coal, evaporite)",
    "carbonate": "Carbonate rock (limestone, dolostone, marlstone)",
    "volcanic": "Volcanic and shallow intrusive rock (basalt, andesite, rhyolite, tuff, dikes)",
    "plutonic": "Plutonic rock (granite, diorite, gabbro, syenite)",
    "metasedimentary": "Metasedimentary rock (quartzite, slate, metasandstone, marble, paragneiss)",
    "crystalline_metamorphic": "Schist, gneiss and other crystalline metamorphic rock (incl. tectonite)",
}
MAJOR_RANKS = ("Major", "Indeterminate, major")


def lith_class(lith1: str, lith2: str) -> str | None:
    """Class of one lithology term from its first two levels; None for ice and unclassifiable rows."""
    l1, l2 = (str(lith1 or "").strip(), str(lith2 or "").strip())
    if l1 == "Unconsolidated":
        return "unconsolidated"
    if l1 == "Sedimentary":
        return "carbonate" if l2 == "Carbonate" else "clastic"
    if l1 == "Igneous":
        return "plutonic" if l2 == "Plutonic" else "volcanic"     # Volcanic, Hypabyssal
    if l1 == "Metamorphic":
        return "metasedimentary" if l2 == "Metasedimentary" else "crystalline_metamorphic"
    if l1 == "Tectonite":
        return "crystalline_metamorphic"
    return None


def unit_class_weights(lith: pd.DataFrame) -> pd.DataFrame:
    """Rows: UNIT_LINK; columns: CLASSES; each row sums to 1 over the unit's classified major lithologies.
    Units with none (ice, water) are absent and count as unmapped."""
    major = lith.loc[lith["LITH_RANK"].isin(MAJOR_RANKS)].copy()
    major["cls"] = [lith_class(a, b) for a, b in zip(major["LITH1"], major["LITH2"])]
    major = major.dropna(subset=["cls"])
    counts = pd.crosstab(major["UNIT_LINK"].astype(str), major["cls"]).reindex(columns=list(CLASSES), fill_value=0)
    return counts.div(counts.sum(axis=1), axis=0)


@dataclass
class UnitGrid(RasterGrid):
    """Raster of map-unit indices (MISSING where unmapped) and of county indices, on one grid."""

    unit: np.ndarray
    county: np.ndarray
    units: np.ndarray    # unit_link for each unit index
    x0: float
    y0: float
    cell: float

    def save(self, path) -> None:
        np.savez_compressed(path, unit=self.unit, county=self.county, units=self.units.astype(str),
                            origin=np.array([self.x0, self.y0, self.cell]))

    @classmethod
    def load(cls, path) -> UnitGrid:
        z = np.load(path)
        x0, y0, cell = z["origin"]
        return cls(z["unit"], z["county"], z["units"], float(x0), float(y0), float(cell))

    def shifted(self, angle_deg: float, dx: float, dy: float, origin: tuple[float, float]) -> np.ndarray:
        """Unit raster of the moved map, read on the unmoved grid (MISSING where moved off the map)."""
        row, col, inside = self.source_cells(angle_deg, dx, dy, origin)
        return np.where(inside, self.unit[row, col], MISSING).astype(np.int32)


class CountyTypeSummary:
    """Rock-type shares per county, over the county's cells that fall on a classified unit."""

    def __init__(self, grid: UnitGrid, weights: pd.DataFrame, county_ids: np.ndarray,
                 centroid_x: np.ndarray, centroid_y: np.ndarray) -> None:
        self.grid = grid
        self.ids = np.asarray(county_ids)
        self.n = len(self.ids)
        # Weight matrix by unit index; unclassified units get a zero row and are skipped.
        w = weights.reindex(pd.Index(grid.units.astype(str))).to_numpy(dtype=float)
        self.classified = np.isfinite(w).all(axis=1)
        self.w = np.nan_to_num(w, nan=0.0)
        flat = grid.county.ravel()
        self._in_county = flat >= 0
        self._owner = flat[self._in_county]
        row, col, inside = grid.cell_of(centroid_x, centroid_y)
        self._fallback = np.where(inside, row * grid.shape[1] + col, -1)
        self._needs_fallback = np.bincount(self._owner, minlength=self.n) == 0

    def summarize(self, unit: np.ndarray | None = None) -> pd.DataFrame:
        unit = (self.grid.unit if unit is None else unit).ravel()
        cells = unit[self._in_county]
        ok = cells >= 0
        ok[ok] = self.classified[cells[ok]]
        owner, u = self._owner[ok], cells[ok]
        n_cells = np.bincount(owner, minlength=self.n).astype(float)
        out = {}
        for k, name in enumerate(CLASSES):
            total = np.bincount(owner, weights=self.w[u, k], minlength=self.n)
            out[f"share_{name}"] = np.divide(total, n_cells, out=np.full(self.n, np.nan), where=n_cells > 0)
        frame = pd.DataFrame(out, index=self.ids)
        frame["type_cells"] = n_cells
        cols = [f"share_{c}" for c in CLASSES]
        for i in np.flatnonzero(self._needs_fallback):
            cell = self._fallback[i]
            if cell < 0 or unit[cell] < 0 or not self.classified[unit[cell]]:
                continue
            frame.iloc[i, [frame.columns.get_loc(c) for c in cols]] = self.w[unit[cell]]
            frame.iloc[i, frame.columns.get_loc("type_cells")] = 1.0
        shares = frame[cols].to_numpy()
        any_ = np.isfinite(shares).all(axis=1)
        top = np.argmax(np.nan_to_num(shares, nan=-1.0), axis=1)
        frame["dominant_type"] = np.where(any_, np.asarray(CLASSES, dtype=object)[top], None)
        return frame


def build_unit_grid(geology, counties, cell_m: float) -> UnitGrid:
    """Rasterize map units (projected GeoDataFrame with unit_link) and counties ('county_index') on one grid."""
    from rasterio import features
    from rasterio.transform import from_origin

    minx, miny, maxx, maxy = counties.total_bounds
    x0, y0 = np.floor(minx / cell_m) * cell_m, np.ceil(maxy / cell_m) * cell_m
    cols = int(np.ceil((maxx - x0) / cell_m))
    rows = int(np.ceil((y0 - miny) / cell_m))
    transform = from_origin(x0, y0, cell_m, cell_m)
    geology = geology.loc[geology.geometry.notna() & ~geology.geometry.is_empty]
    codes, units = pd.factorize(geology["unit_link"].astype(str), sort=True)
    unit = features.rasterize(zip(geology.geometry, codes.astype("int32")), out_shape=(rows, cols),
                              transform=transform, fill=MISSING, dtype="int32")
    county = features.rasterize(zip(counties.geometry, counties["county_index"].astype("int32")), out_shape=(rows, cols),
                                transform=transform, fill=MISSING, dtype="int32")
    return UnitGrid(unit, county, np.asarray(units, dtype=str), float(x0), float(y0), float(cell_m))
