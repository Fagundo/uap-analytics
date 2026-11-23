"""Year by year: what share of a sighting set falls near each program site?

The shuffle tests detect any clustering in space and time, including a local wave that has nothing to do with a
program. This table lets a reader check whether a site's share rises when its program starts and falls when it
ends, against the site's own history.
"""
from __future__ import annotations

from collections import Counter

from uap_geo.replications.common.geo import haversine_km
from uap_geo.replications.programs.catalog import Program, Site
from uap_geo.replications.programs.sightings import Sighting


def program_sites(programs: list[Program]) -> list[Site]:
    """Each distinct site once, in catalog order."""
    return list({(s.name, s.lat, s.lon): s for p in programs for s in p.sites}.values())


def local_share_by_year(sightings: list[Sighting], sites: list[Site], radius_km: float = 300.0) -> dict:
    located = [s for s in sightings if s.lat is not None and s.lon is not None]
    total = Counter(s.date.start.year for s in located)
    out = {}
    for site in sites:
        near = Counter(s.date.start.year for s in located if haversine_km(s.lat, s.lon, site.lat, site.lon) <= radius_km)
        out[site.name] = [{"year": y, "all": total[y], "near": near[y],
                           "share": round(near[y] / total[y], 4) if total[y] else 0.0} for y in sorted(total)]
    return out
