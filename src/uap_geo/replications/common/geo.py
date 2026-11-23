"""Great-circle distance on a spherical Earth (the same formula and radius as the original tests)."""
from __future__ import annotations

import math

EARTH_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p = math.pi / 180
    a = math.sin((lat2 - lat1) * p / 2) ** 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lon2 - lon1) * p / 2) ** 2
    return 2 * EARTH_KM * math.asin(math.sqrt(a))
