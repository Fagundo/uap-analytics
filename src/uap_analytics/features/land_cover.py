"""County shares of NLCD land-cover groups."""

from __future__ import annotations

import numpy as np
import pandas as pd

# NLCD class codes grouped; open water (11), ice (12) and barren (31) are left out (the reference).
GROUPS: dict[str, tuple[int, ...]] = {
    "developed": (21, 22, 23, 24),
    "forest": (41, 42, 43),
    "shrub_grass": (52, 71),
    "pasture": (81,),
    "cropland": (82,),
    "wetland": (90, 95),
}


def group_shares(codes: np.ndarray, owner: np.ndarray, n: int) -> pd.DataFrame:
    """Share of each group among a county's land-cover cells with a valid class. codes and owner are flat
    arrays of the same length (owner = county index, -1 outside)."""
    valid = (owner >= 0) & (codes > 0) & (codes < 250)
    c, o = codes[valid], owner[valid]
    total = np.bincount(o, minlength=n).astype(float)
    out = {}
    for name, members in GROUPS.items():
        hits = np.bincount(o[np.isin(c, members)], minlength=n).astype(float)
        out[f"lc_{name}"] = np.divide(hits, total, out=np.full(n, np.nan), where=total > 0)
    frame = pd.DataFrame(out)
    frame["lc_cells"] = total
    return frame


def county_land_cover(tif_path, counties, county_ids) -> pd.DataFrame:
    """Rasterize counties onto the land-cover grid and compute group shares; index = county_ids.
    `counties` must be in the raster's CRS, in the same order as county_ids."""
    import rasterio
    from rasterio import features

    with rasterio.open(tif_path) as src:
        codes = src.read(1)
        transform, shape = src.transform, (src.height, src.width)
    owner = features.rasterize(zip(counties.geometry, np.arange(len(counties), dtype="int32")), out_shape=shape,
                               transform=transform, fill=-1, dtype="int32", all_touched=False)
    frame = group_shares(codes.ravel().astype(np.int32), owner.ravel(), len(counties))
    frame.index = pd.Index(county_ids)
    return frame
