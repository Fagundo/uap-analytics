"""County summaries of the age of the rocks at the surface, from a geologic map rasterized onto a regular
grid in the study's equal-area CRS.

Each grid cell carries the log10 midpoint age (Ma) of the map unit covering it and that age's era. A
county's mean log age and era shares are averages over its cells; a county smaller than a cell takes the
cell under its centroid. The grid also makes the layer-shift test cheap: a rotated and shifted copy of the
map is read by mapping every cell centre back through the inverse motion (nearest cell).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

# Era boundaries (Ma), International Chronostratigraphic Chart; a unit's era is that of its midpoint age.
ERAS: tuple[tuple[str, float, float], ...] = (
    ("cenozoic", 0.0, 66.0),
    ("mesozoic", 66.0, 251.9),
    ("paleozoic", 251.9, 538.8),
    ("precambrian", 538.8, np.inf),
)
ERA_NAMES = tuple(e[0] for e in ERAS)
MISSING = -1


def era_codes(mid_ma: np.ndarray) -> np.ndarray:
    """Index into ERAS for each midpoint age; MISSING where the age is not finite."""
    mid = np.asarray(mid_ma, dtype=float)
    edges = np.array([e[1] for e in ERAS[1:]])
    codes = np.searchsorted(edges, mid, side="right").astype(np.int8)
    codes[~np.isfinite(mid)] = MISSING
    return codes


class RasterGrid:
    """A north-up grid: x0, y0 = left and top edges, cell = side in metres. Subclasses hold the rasters."""

    x0: float
    y0: float
    cell: float

    @property
    def shape(self) -> tuple[int, int]:
        return self.county.shape

    def centres(self) -> tuple[np.ndarray, np.ndarray]:
        rows, cols = self.shape
        x = self.x0 + (np.arange(cols) + 0.5) * self.cell
        y = self.y0 - (np.arange(rows) + 0.5) * self.cell
        return np.meshgrid(x, y)

    def cell_of(self, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """(row, col, inside) of the cells containing points (x, y)."""
        col = np.floor((np.asarray(x) - self.x0) / self.cell).astype(np.int64)
        row = np.floor((self.y0 - np.asarray(y)) / self.cell).astype(np.int64)
        rows, cols = self.shape
        inside = (row >= 0) & (row < rows) & (col >= 0) & (col < cols)
        return np.clip(row, 0, rows - 1), np.clip(col, 0, cols - 1), inside

    def source_cells(self, angle_deg: float, dx: float, dy: float, origin: tuple[float, float]):
        """For a copy of the map rotated by angle_deg about origin and translated by (dx, dy): the (row, col,
        inside) of the original cell each unmoved cell now shows (nearest cell; inside False = off the map)."""
        xc, yc = self.centres()
        ox, oy = origin
        # Inverse motion: undo the translation, then rotate back by -angle about the origin.
        u, v = xc - dx - ox, yc - dy - oy
        a = np.deg2rad(-angle_deg)
        xs = ox + u * np.cos(a) - v * np.sin(a)
        ys = oy + u * np.sin(a) + v * np.cos(a)
        return self.cell_of(xs, ys)


@dataclass
class AgeGrid(RasterGrid):
    """Rasters on one grid: log10 age (NaN where undated), era code, and county index (MISSING outside)."""

    log_age: np.ndarray
    era: np.ndarray
    county: np.ndarray
    x0: float           # x of the left edge of column 0
    y0: float           # y of the top edge of row 0
    cell: float         # metres

    def save(self, path) -> None:
        np.savez_compressed(path, log_age=self.log_age.astype("float32"), era=self.era, county=self.county,
                            origin=np.array([self.x0, self.y0, self.cell]))

    @classmethod
    def load(cls, path) -> AgeGrid:
        z = np.load(path)
        x0, y0, cell = z["origin"]
        return cls(z["log_age"].astype(float), z["era"], z["county"], float(x0), float(y0), float(cell))

    def shifted(self, angle_deg: float, dx: float, dy: float, origin: tuple[float, float]) -> tuple[np.ndarray, np.ndarray]:
        """(log_age, era) of the map after rotating it by angle_deg about origin and translating by (dx, dy),
        read on the unmoved grid. Cells whose source falls outside the map come back missing."""
        row, col, inside = self.source_cells(angle_deg, dx, dy, origin)
        log_age = np.where(inside, self.log_age[row, col], np.nan)
        era = np.where(inside, self.era[row, col], MISSING).astype(np.int8)
        return log_age, era


class CountyAgeSummary:
    """Mean log10 age and era shares per county, over the county's dated cells."""

    def __init__(self, grid: AgeGrid, county_ids: np.ndarray, centroid_x: np.ndarray, centroid_y: np.ndarray) -> None:
        self.grid = grid
        self.ids = np.asarray(county_ids)
        self.n = len(self.ids)
        flat = grid.county.ravel()
        self._in_county = flat >= 0
        self._county_of_cell = flat[self._in_county]
        counts = np.bincount(self._county_of_cell, minlength=self.n)
        # Counties smaller than a cell take the cell under their centroid.
        row, col, inside = grid.cell_of(centroid_x, centroid_y)
        self._fallback = np.where(inside, row * grid.shape[1] + col, -1)
        self._needs_fallback = counts == 0

    def summarize(self, log_age: np.ndarray | None = None, era: np.ndarray | None = None) -> pd.DataFrame:
        log_age = self.grid.log_age if log_age is None else log_age
        era = self.grid.era if era is None else era
        la = log_age.ravel()
        er = era.ravel()
        cells_age, cells_era, owner = la[self._in_county], er[self._in_county], self._county_of_cell
        dated = np.isfinite(cells_age)
        n_dated = np.bincount(owner[dated], minlength=self.n).astype(float)
        total = np.bincount(owner[dated], weights=cells_age[dated], minlength=self.n)
        out = {"rock_log10_age": np.divide(total, n_dated, out=np.full(self.n, np.nan), where=n_dated > 0)}
        for k, name in enumerate(ERA_NAMES):
            hits = np.bincount(owner[cells_era == k], minlength=self.n).astype(float)
            out[f"share_{name}"] = np.divide(hits, n_dated, out=np.full(self.n, np.nan), where=n_dated > 0)
        frame = pd.DataFrame(out, index=self.ids)
        frame["rock_cells"] = n_dated
        for i in np.flatnonzero(self._needs_fallback):
            cell = self._fallback[i]
            if cell < 0 or not np.isfinite(la[cell]):
                continue
            frame.iloc[i, frame.columns.get_loc("rock_log10_age")] = la[cell]
            for k, name in enumerate(ERA_NAMES):
                frame.iloc[i, frame.columns.get_loc(f"share_{name}")] = float(er[cell] == k)
            frame.iloc[i, frame.columns.get_loc("rock_cells")] = 1.0
        shares = frame[[f"share_{n}" for n in ERA_NAMES]].to_numpy()
        dated_any = np.isfinite(shares).all(axis=1)
        top = np.argmax(np.nan_to_num(shares, nan=-1.0), axis=1)
        frame["dominant_era"] = np.where(dated_any, np.asarray(ERA_NAMES, dtype=object)[top], None)
        return frame


def build_age_grid(geology, counties, cell_m: float) -> AgeGrid:
    """Rasterize map units (projected GeoDataFrame with log10_age and mid_ma) and counties onto one grid.

    `counties` must be projected the same way and carry a positional index 0..n-1 in column 'county_index'.
    Where map polygons overlap (state seams), the later polygon wins; the overlap is a small share of cells."""
    from rasterio import features
    from rasterio.transform import from_origin

    minx, miny, maxx, maxy = counties.total_bounds
    x0, y0 = np.floor(minx / cell_m) * cell_m, np.ceil(maxy / cell_m) * cell_m
    cols = int(np.ceil((maxx - x0) / cell_m))
    rows = int(np.ceil((y0 - miny) / cell_m))
    transform = from_origin(x0, y0, cell_m, cell_m)

    dated = geology.loc[np.isfinite(geology["log10_age"]) & geology.geometry.notna() & ~geology.geometry.is_empty]
    log_age = features.rasterize(zip(dated.geometry, dated["log10_age"].astype("float32")), out_shape=(rows, cols),
                                 transform=transform, fill=np.nan, dtype="float32")
    era = era_codes(np.power(10.0, log_age.astype(float)))
    county = features.rasterize(zip(counties.geometry, counties["county_index"].astype("int32")), out_shape=(rows, cols),
                                transform=transform, fill=MISSING, dtype="int32")
    return AgeGrid(log_age.astype(float), era, county, float(x0), float(y0), float(cell_m))
