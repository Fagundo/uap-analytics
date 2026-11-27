"""Distances, bearings and lines of sight on a spherical Earth."""
from __future__ import annotations

import math

EARTH_KM = 6371.0
REFRACTION_K = 0.13          # typical optical refraction coefficient: light bends to follow the curve a little


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p = math.pi / 180
    a = math.sin((lat2 - lat1) * p / 2) ** 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lon2 - lon1) * p / 2) ** 2
    return 2 * EARTH_KM * math.asin(math.sqrt(a))


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Initial compass bearing from point 1 to point 2."""
    p1, p2, dl = math.radians(lat1), math.radians(lat2), math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return math.degrees(math.atan2(y, x)) % 360


def angle_diff(a: float, b: float) -> float:
    """Smallest difference between two compass directions, 0-180."""
    return abs((a - b + 180) % 360 - 180)


def curvature_drop_m(distance_km: float, k: float = REFRACTION_K) -> float:
    """How far the Earth's surface falls below a level line at this distance, allowing for refraction."""
    return (distance_km * 1000) ** 2 / (2 * EARTH_KM * 1000 / (1 - k))


def elevation_angle_deg(distance_km: float, target_m: float, observer_m: float = 0.0) -> float:
    """Apparent angle above the horizontal of a target at this distance and height (both above sea level)."""
    return math.degrees(math.atan2(target_m - observer_m - curvature_drop_m(distance_km), distance_km * 1000))


def height_for_angle_m(distance_km: float, angle_deg: float, observer_m: float = 0.0) -> float:
    """Height above sea level a target at this distance needs to appear at this angle."""
    return observer_m + distance_km * 1000 * math.tan(math.radians(angle_deg)) + curvature_drop_m(distance_km)


def line_of_sight_km(height_m: float, observer_m: float = 0.0) -> float:
    """Farthest distance at which an object this high is above the observer's horizon."""
    r = EARTH_KM * 1000 / (1 - REFRACTION_K)
    return (math.sqrt(2 * r * max(height_m, 0)) + math.sqrt(2 * r * max(observer_m, 0))) / 1000
