"""Nuclear test explosions grouped into test sites."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date

from uap_geo.replications.common.geo import haversine_km


@dataclass(frozen=True)
class NuclearTest:
    id: str
    day: date
    country: str
    kind: str                                     # air | underground | water
    lat: float
    lon: float
    name: str = ""


@dataclass(frozen=True)
class TestSite:
    """Tests within ``radius_km`` of each other, grouped greedily (most-used locations first)."""
    id: str
    country: str
    lat: float
    lon: float
    tests: tuple[NuclearTest, ...]

    __test__ = False                              # not a pytest test class

    @property
    def label(self) -> str:
        ns = "N" if self.lat >= 0 else "S"
        ew = "E" if self.lon >= 0 else "W"
        return f"{self.country} site near {abs(self.lat):.1f}°{ns} {abs(self.lon):.1f}°{ew}"


def group_sites(tests: list[NuclearTest], radius_km: float = 150.0) -> list[TestSite]:
    """Group tests into sites. A test joins the nearest site centre within the radius; centres are the most-used
    locations (0.1 degree), each at least ``radius_km`` from the centres before it."""
    counts = Counter((round(t.lat, 1), round(t.lon, 1)) for t in tests)
    centres: list[tuple[float, float]] = []
    for (lat, lon), _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        if all(haversine_km(lat, lon, a, b) > radius_km for a, b in centres):
            centres.append((lat, lon))
    groups: dict[int, list[NuclearTest]] = {}
    for t in tests:
        i = min(range(len(centres)), key=lambda k: haversine_km(t.lat, t.lon, *centres[k]))
        if haversine_km(t.lat, t.lon, *centres[i]) <= radius_km:
            groups.setdefault(i, []).append(t)
    sites = []
    for i, ts in groups.items():
        country = Counter(t.country for t in ts).most_common(1)[0][0]
        lat = sum(t.lat for t in ts) / len(ts)
        lon = sum(t.lon for t in ts) / len(ts)
        sites.append(TestSite(f"site{i}", country, round(lat, 3), round(lon, 3), tuple(sorted(ts, key=lambda t: t.day))))
    return sorted(sites, key=lambda s: (-len(s.tests), s.id))
