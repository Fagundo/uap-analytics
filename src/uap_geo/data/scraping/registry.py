"""Builds DataSource objects from config, so the pipeline never names concrete classes."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from uap_geo.common.base import DataSource
from uap_geo.common.config import Config
from uap_geo.common.download import Downloader
from uap_geo.data.scraping.census import (
    CountySource,
    GazetteerSource,
    MilitarySource,
    PopulationSource,
)
from uap_geo.data.scraping.acs import AcsShareSource
from uap_geo.data.scraping.other import (
    AirportSource,
    ConfiguredSitesSource,
    NaturalEarthSource,
    NuclearPlantSource,
    RasterSource,
    ReservoirSource,
    ScienceBasePointsSource,
    ScienceBaseRasterSource,
)
from uap_geo.data.scraping.nlcd import NlcdLandCoverSource
from uap_geo.data.scraping.sgmc import SgmcGeologySource
from uap_geo.data.scraping.volcanoes import HoloceneVolcanoSource
from uap_geo.data.scraping.usgs import EarthquakeSource, QuaternaryFaultSource

RASTER_SOURCES = ("light_pollution", "cloud_cover", "tree_canopy", "magnetic_anomaly")
EXPORT_PIN = Path("configs/pursue_export.yaml")


class _FromExport:
    """A DataSource-shaped wrapper: ``load()`` returns a table built from the PURSUE export."""

    def __init__(self, build: Callable[[], object]) -> None:
        self._build = build

    def load(self):
        return self._build()


class SourceRegistry:
    """Sightings, launches, Kp and quakes come from PURSUE's export (configs/pursue_export.yaml); uap-geo no
    longer fetches or cleans them itself (data refactor, Phase 4)."""

    def __init__(self, config: Config, downloader: Downloader) -> None:
        self._config = config
        self._dl = downloader
        self._export = None

    def export_tables(self):
        """The pinned PURSUE export as uap-geo's tables."""
        if self._export is None:
            from uap_geo.data.scraping.pursue_export import ExportPin, ExportTables, PursueExport
            self._export = ExportTables(PursueExport(ExportPin.load(EXPORT_PIN), self._config.paths.raw))
        return self._export

    def cleaned_reports(self, years: tuple[int, int]):
        """NUFORC reports for the years, cleaned (frame, CleaningReport)."""
        return self.export_tables().reports(years)

    def kp(self):
        """Daily maximum Kp (``load()`` -> Series indexed by UTC date)."""
        return _FromExport(self.export_tables().kp_daily)

    def quakes(self, first_year: int, last_year: int, min_magnitude: float):
        """ComCat events (``load()`` -> GeoDataFrame time, latitude, longitude, mag, geometry). The export holds
        M3.0+ from 2001; other requests (the v1 county pipeline's M2.5) use uap-geo's own loader."""
        if min_magnitude >= 3.0 and first_year >= 2001:
            tables = self.export_tables()
            def build():
                import geopandas as gpd
                q = tables.quakes(first_year, last_year, min_magnitude)
                return gpd.GeoDataFrame(q, geometry=gpd.points_from_xy(q["longitude"], q["latitude"]), crs="EPSG:4326")
            return _FromExport(build)
        return EarthquakeSource(self._config.source("earthquakes"), self._dl, first_year, last_year, min_magnitude)

    @property
    def downloader(self) -> Downloader:
        return self._dl

    def is_active(self, name: str) -> bool:
        return name in self._config.sources and self._config.source(name).is_active

    def counties(self) -> CountySource:
        return CountySource(self._config.source("counties"), self._dl)

    def historical_population(self, years: tuple[int, ...]):
        """Mean county population over the given censuses (1900-1990), on today's county ids."""
        from uap_geo.data.scraping.census_history import HistoricalPopulationSource
        return HistoricalPopulationSource(self._config.source("hist_population"), self._dl, years)

    def census_population(self, year: int):
        """County totals of the 2000 or 2010 census (``load()`` -> Series by today's county id)."""
        from uap_geo.data.scraping.census_history import DecennialApiPopulation
        return DecennialApiPopulation(self._config.source("pop2000"), self._dl, year)

    def population(self) -> PopulationSource:
        return PopulationSource(self._config.source("population"), self._dl)

    def gazetteers(self) -> list[GazetteerSource]:
        return [
            GazetteerSource(self._config.source("gazetteer_places"), self._dl, "place"),
            GazetteerSource(self._config.source("gazetteer_cousubs"), self._dl, "cousub"),
        ]

    def place_points(self):
        """Census places (cities, towns, CDPs) as points: the settlement-density control."""
        import geopandas as gpd

        from uap_geo.common.geo import WGS84

        places = self.gazetteers()[0].load().dropna(subset=["lat", "lon"])
        places = places.merge(self.place_population(), on="place_geoid", how="left")
        return gpd.GeoDataFrame(places, geometry=gpd.points_from_xy(places["lon"], places["lat"]), crs=WGS84)

    def place_population(self):
        """Incorporated-place population (empty frame if no configured vintage could be read)."""
        import logging

        import pandas as pd

        from uap_geo.data.scraping.parsers import parse_place_population

        log = logging.getLogger(__name__)
        empty = pd.DataFrame(columns=["place_geoid", "place_population"])
        if not self.is_active("place_population"):
            return empty
        config = self._config.source("place_population")
        for index, url in enumerate(config.urls):
            try:
                path = self._dl.fetch(config, f"place_population_{index}.csv", url_index=index)
                frame = parse_place_population(path.read_bytes())
                log.info("Place population: %d incorporated places from %s", len(frame), url)
                return frame
            except Exception as exc:
                log.warning("Place population source failed (%s): %s", url, exc)
        return empty

    def primary_roads(self) -> NaturalEarthSource:
        return NaturalEarthSource(self._config.source("primary_roads"), self._dl)

    def rail(self) -> NaturalEarthSource:
        return NaturalEarthSource(self._config.source("rail"), self._dl)

    def airports(self) -> AirportSource:
        return AirportSource(self._config.source("airports"), self._dl)

    def military(self) -> MilitarySource:
        return MilitarySource(self._config.source("military"), self._dl)

    def faults(self) -> QuaternaryFaultSource:
        return QuaternaryFaultSource(self._config.source("faults"), self._dl)

    def earthquakes(self) -> EarthquakeSource:
        study = self._config.study
        return EarthquakeSource(
            self._config.source("earthquakes"), self._dl, study.start_year, study.end_year, study.min_quake_magnitude
        )

    def rivers(self) -> NaturalEarthSource:
        return NaturalEarthSource(self._config.source("rivers"), self._dl)

    def lakes(self) -> NaturalEarthSource:
        return NaturalEarthSource(self._config.source("lakes"), self._dl)

    def coastline(self) -> NaturalEarthSource:
        return NaturalEarthSource(self._config.source("coastline"), self._dl)

    def reservoirs(self) -> ReservoirSource:
        return ReservoirSource(self._config.source("reservoirs"), self._dl, self._config.study.min_reservoir_acre_ft)

    def gamma_rays(self) -> ScienceBasePointsSource:
        return ScienceBasePointsSource(self._config.source("gamma_rays"), self._dl)

    def nuclear_power(self) -> NuclearPlantSource:
        return NuclearPlantSource(self._config.source("nuclear_power"), self._dl)

    def weapons_sites(self) -> ConfiguredSitesSource:
        return ConfiguredSitesSource(self._config.source("weapons_sites"), self._dl)

    def seasonal_housing(self) -> AcsShareSource:
        """Share of housing units vacant for seasonal, recreational or occasional use (tourism)."""
        return AcsShareSource(self._config.source("acs_housing"), self._dl, "seasonal_housing_share",
                              ("B25004_E006",), "B25001_E001")

    def college_enrollment(self) -> AcsShareSource:
        """Share of residents aged 3+ enrolled in college, undergraduate or graduate (college towns)."""
        return AcsShareSource(self._config.source("acs_college"), self._dl, "college_enrolled_share",
                              ("B14001_E008", "B14001_E009"), "B14001_E001")

    def volcanoes(self) -> HoloceneVolcanoSource:
        return HoloceneVolcanoSource(self._config.source("volcanoes"), self._dl)

    def land_cover(self) -> NlcdLandCoverSource:
        """NLCD 2011 land cover at 480 m (GeoTIFF path)."""
        return NlcdLandCoverSource(self._config.source("nlcd_2011"), self._dl)

    def geologic_map(self) -> SgmcGeologySource:
        """USGS State Geologic Map Compilation: map-unit polygons with their age range."""
        return SgmcGeologySource(self._config.source("sgmc"), self._dl)

    def launches(self, min_apogee_km: float = 100.0):
        """GCAT launches from contiguous-U.S. sites, timed, orbital or reaching min_apogee_km."""
        tables = self.export_tables()
        return _FromExport(lambda: tables.launches(min_apogee_km))

    def raster(self, name: str) -> RasterSource:
        return RasterSource(self._config.source(name), self._dl)
