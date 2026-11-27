"""U.S. states: outlines (data/reference/us_states.geojson), names and codes, point-in-state and centroids."""
from __future__ import annotations

import json
import re
from pathlib import Path

from uap_analytics.common.geo import STATE_NAME_TO_CODE

DEFAULT_OUTLINES = Path(__file__).resolve().parents[4] / "data" / "reference" / "us_states.geojson"

# The original test's text placement for PURSUE incidents (location text -> one state), kept as it was
ABBREVIATIONS = {"N.M.": "New Mexico", "NM": "New Mexico", "TX": "Texas", "AZ": "Arizona", "Ariz": "Arizona",
                 "CA": "California", "Calif": "California", "NV": "Nevada", "Nev": "Nevada", "UT": "Utah",
                 "D.C.": "District of Columbia", "DC": "District of Columbia", "N.J.": "New Jersey", "AR": "Arkansas",
                 "KS": "Kansas", "CO": "Colorado", "Ky.": "Kentucky", "S.C.": "South Carolina",
                 "S.D.": "South Dakota", "N.D.": "North Dakota", "Mich": "Michigan", "Wash": "Washington"}
SITES = {"los alamos": "New Mexico", "sandia": "New Mexico", "starvation peak": "New Mexico",
         "white sands": "New Mexico", "holloman": "New Mexico", "kirtland": "New Mexico", "pantex": "Texas",
         "andrews field": "Maryland", "rapid city": "South Dakota", "godman": "Kentucky",
         "anacostia": "District of Columbia", "groom lake": "Nevada", "tonopah": "Nevada",
         "area 51": "Nevada", "edwards": "California", "muroc": "California"}


class StatePlacer:
    """State outlines by name; coordinates -> the state containing them; a state's centroid."""

    def __init__(self, states_geojson: Path = DEFAULT_OUTLINES):
        gj = json.loads(Path(states_geojson).read_text())
        self._polys: list[tuple[str, list[list[tuple[float, float]]]]] = []
        for f in gj["features"]:
            name, geom = f["properties"]["n"], f["geometry"]
            polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
            for poly in polys:
                self._polys.append((name, [list(map(tuple, ring)) for ring in poly]))
        self.names = sorted({n for n, _ in self._polys}, key=len, reverse=True)
        self._by_code = {STATE_NAME_TO_CODE[n.lower()]: n for n in self.names if n.lower() in STATE_NAME_TO_CODE}

    def name(self, code: str | None) -> str | None:
        """USPS code (as the export writes states) -> the state's name (as the program catalog lists them)."""
        return self._by_code.get(code) if code else None

    def from_text(self, text: str | None) -> str | None:
        """Free text -> one state, when exactly one state (by name, abbreviation or known site) is named."""
        if not text:
            return None
        hits = [n for n in self.names if re.search(r"\b" + re.escape(n) + r"\b", text, re.IGNORECASE)]
        hits += [n for a, n in ABBREVIATIONS.items() if re.search(r"(?<![A-Za-z])" + re.escape(a) + r"(?![A-Za-z])", text)]
        low = text.lower()
        hits += [n for site, n in SITES.items() if site in low]
        hits = list(dict.fromkeys(hits))
        if "Washington" in hits and re.search(r"D\.?\s?C\b", text):
            hits = [h for h in hits if h != "Washington"] or ["District of Columbia"]
        if "New Mexico" in hits and "Mexico" in hits:
            hits.remove("Mexico")
        return hits[0] if len(hits) == 1 else None

    def centroid(self, state: str) -> tuple[float, float] | None:
        """Area-weighted centre of a state's largest polygon (lat, lon)."""
        best, best_area = None, 0.0
        for name, rings in self._polys:
            if name != state:
                continue
            ring = rings[0]
            a = cx = cy = 0.0
            for (x1, y1, *_), (x2, y2, *_) in zip(ring, ring[1:] + ring[:1]):
                cross = x1 * y2 - x2 * y1
                a += cross
                cx += (x1 + x2) * cross
                cy += (y1 + y2) * cross
            if a and abs(a) > best_area:
                best_area, best = abs(a), (cy / (3 * a), cx / (3 * a))
        return best

    def from_point(self, lat: float, lon: float) -> str | None:
        for name, rings in self._polys:
            if _inside(lon, lat, rings[0]) and not any(_inside(lon, lat, hole) for hole in rings[1:]):
                return name
        return None


def _inside(x: float, y: float, ring: list[tuple[float, float]]) -> bool:
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][:2]
        xj, yj = ring[j][:2]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside
