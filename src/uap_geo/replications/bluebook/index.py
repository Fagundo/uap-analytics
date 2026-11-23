"""Blue Book case index rows as the shift test needs them, and their coverage of the Air Force's totals."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

# Cases per year (all, unidentified) as the Air Force reported them (USAF fact sheet, usaf_f1.pdf)
OFFICIAL = {1947: (122, 12), 1948: (156, 7), 1949: (186, 22), 1950: (210, 27), 1951: (169, 22), 1952: (1501, 303),
            1953: (509, 42), 1954: (487, 46), 1955: (545, 24), 1956: (670, 14), 1957: (1006, 14), 1958: (627, 10),
            1959: (390, 12), 1960: (557, 14), 1961: (591, 13), 1962: (474, 15), 1963: (399, 14), 1964: (562, 19),
            1965: (887, 16), 1966: (1112, 32), 1967: (937, 19), 1968: (375, 3), 1969: (146, 1)}
OFFICIAL_SOURCE = "https://www.esd.whs.mil/Portals/54/Documents/FOID/Reading%20Room/UFOsandUAPs/usaf_f1.pdf"


@dataclass(frozen=True)
class IndexRow:
    year: int
    month: int
    state: str | None                             # state name
    country: str | None
    category: str                                 # astro | aircraft | balloon | satellite | other | insufficient | unidentified
    family: str | None                            # for explained cases, the kind of cause named


def coverage(rows: list[IndexRow]) -> list[dict]:
    """Rows recovered per year against the Air Force's totals."""
    n = Counter(r.year for r in rows)
    unid = Counter(r.year for r in rows if r.category == "unidentified")
    located = Counter(r.year for r in rows if r.state or r.country)
    return [{"year": y, "official": tot, "recovered": n[y], "share": round(n[y] / tot, 2),
             "with_place": located[y], "unidentified_official": u, "unidentified_recovered": unid[y]}
            for y, (tot, u) in sorted(OFFICIAL.items())]
