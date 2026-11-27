"""County population by decennial census, 1900-1990 (U.S. Census Bureau, compiled by Richard L. Forstall;
CSV from NBER, data.nber.org/census/population/cencounts).

Counties are 1990 counties with their FIPS codes. ``HistoricalPopulationSource.load`` returns today's county
ids with the mean population over the requested censuses, after carrying 1990 counties onto today's:

* renamed codes: Dade, FL 12025 -> Miami-Dade 12086 (1997); Shannon, SD 46113 -> Oglala Lakota 46102 (2015);
* merged independent cities, added to the county that absorbed them: South Boston, VA 51780 -> Halifax 51083
  (1995), Clifton Forge, VA 51560 -> Alleghany 51005 (2001), Bedford city, VA 51515 -> Bedford 51019 (2013);
* Yellowstone National Park, MT 30113 (merged into Gallatin and Park in 1997, a few hundred people) is dropped.

Counties created after 1990 (Broomfield, CO 08014) have no history and come back missing. A county absent in
an early census (created later) is averaged over the censuses it has.
"""

from __future__ import annotations

import logging
import re

import pandas as pd

from uap_analytics.common.base import DataSource
from uap_analytics.common.config import SourceConfig
from uap_analytics.common.download import Downloader
from uap_analytics.common.geo import COUNTY_ID

log = logging.getLogger(__name__)

RENAMED = {"12025": "12086", "46113": "46102"}
MERGED = {"51780": "51083", "51560": "51005", "51515": "51019"}
DROPPED = {"30113"}


def parse_cencounts(frame: pd.DataFrame) -> pd.DataFrame:
    """(county id, census year) -> population, from the NBER CSV whatever its exact column names: one FIPS
    column and one column per census year (a 4-digit year in the name). State and national rows (county part
    000) are dropped."""
    cols = {c.lower(): c for c in frame.columns}
    fips_col = next((cols[c] for c in cols if "fips" in c), None)
    if fips_col is None:
        raise ValueError(f"No FIPS column in {list(frame.columns)}")
    years = {int(m.group(1)): c for c in frame.columns if (m := re.search(r"(1[89]\d0)", str(c)))}
    if not years:
        raise ValueError(f"No census-year columns in {list(frame.columns)}")
    fips = pd.to_numeric(frame[fips_col], errors="coerce").dropna().astype(int).astype(str).str.zfill(5)
    data = frame.loc[fips.index]
    long = []
    for year, col in sorted(years.items()):
        pop = pd.to_numeric(data[col].astype(str).str.replace(",", ""), errors="coerce")
        long.append(pd.DataFrame({COUNTY_ID: fips.to_numpy(), "year": year, "population": pop.to_numpy()}))
    out = pd.concat(long, ignore_index=True)
    return out.loc[~out[COUNTY_ID].str.endswith("000")]


def to_current_counties(long: pd.DataFrame) -> pd.DataFrame:
    """Carry 1990 county codes onto today's (renames, merged cities summed into their county)."""
    out = long.loc[~long[COUNTY_ID].isin(DROPPED)].copy()
    out[COUNTY_ID] = out[COUNTY_ID].replace({**RENAMED, **MERGED})
    return out.groupby([COUNTY_ID, "year"], as_index=False)["population"].sum(min_count=1)


def mean_population(long: pd.DataFrame, years: tuple[int, ...]) -> pd.DataFrame:
    sub = long.loc[long["year"].isin(years) & (long["population"] > 0)]
    agg = sub.groupby(COUNTY_ID)["population"].agg(["mean", "count"])
    return agg.rename(columns={"mean": "population_hist", "count": "censuses"}).reset_index()


class HistoricalPopulationSource(DataSource):
    def __init__(self, config: SourceConfig, downloader: Downloader, years: tuple[int, ...]) -> None:
        super().__init__(config, downloader)
        self.years = tuple(years)

    def by_census(self) -> pd.DataFrame:
        """Today's county ids x census year (1900-1990) -> population."""
        frame = pd.read_csv(self.downloader.fetch_url(self.name, self.config.urls[0], "cencounts.csv"), dtype=str)
        long = to_current_counties(parse_cencounts(frame))
        return long.pivot_table(index=COUNTY_ID, columns="year", values="population", aggfunc="sum")

    def load(self) -> pd.DataFrame:
        path = self.downloader.fetch_url(self.name, self.config.urls[0], "cencounts.csv")
        frame = pd.read_csv(path, dtype=str)
        log.info("Census 1900-1990 county counts: %d rows, columns %s", len(frame), list(frame.columns)[:14])
        out = mean_population(to_current_counties(parse_cencounts(frame)), self.years)
        log.info("Historical population (%s): %d counties", "/".join(map(str, self.years)), len(out))
        return out


class DecennialApiPopulation(DataSource):
    """County population at the 2000 and 2010 censuses from the Census Bureau's 2000-2010 intercensal county
    file (co-est00int-tot.csv): ESTIMATESBASE2000 (the April 2000 census base) and CENSUS2010POP; on today's
    county ids."""

    COLUMNS = {2000: "ESTIMATESBASE2000", 2010: "CENSUS2010POP"}

    def __init__(self, config: SourceConfig, downloader: Downloader, year: int) -> None:
        super().__init__(config, downloader)
        self.year = year

    def load(self) -> pd.Series:
        path = self.downloader.fetch_url(self.name, self.config.urls[0], "co-est00int-tot.csv")
        frame = pd.read_csv(path, dtype=str, encoding="latin-1")
        frame = frame.loc[frame["COUNTY"].astype(int) != 0]
        long = pd.DataFrame({COUNTY_ID: frame["STATE"].str.zfill(2) + frame["COUNTY"].str.zfill(3), "year": self.year,
                             "population": pd.to_numeric(frame[self.COLUMNS[self.year]], errors="coerce")})
        out = to_current_counties(long)
        return out.set_index(COUNTY_ID)["population"].rename(self.year)
