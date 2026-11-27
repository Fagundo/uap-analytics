"""NLCD 2011 land cover (USGS MRLC), conterminous US, fetched from the MRLC WCS at 480 m (scale factor 1/16,
nearest neighbour), EPSG:5070. 2011 sits mid-way through the 2001-2023 reports. Classes keep NLCD codes."""

from __future__ import annotations

from pathlib import Path

from uap_analytics.common.base import DataSource

FILENAME = "nlcd_2011_land_cover_l48_480m.tif"


class NlcdLandCoverSource(DataSource):
    def load(self) -> Path:
        return self.downloader.fetch(self.config, FILENAME)
