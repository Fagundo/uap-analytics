"""One sighting to test: when, in which state (or country), and where, when the source gives coordinates."""
from __future__ import annotations

from dataclasses import dataclass

from uap_analytics.replications.common.dates import Span


@dataclass(frozen=True)
class Sighting:
    id: str
    date: Span
    state: str                                    # state name; with world=True the country outside the U.S.
    source: str
    group: str = ""                               # a block for sensitivity checks (document, or state:year)
    lat: float | None = None
    lon: float | None = None


def one_per(sightings: list[Sighting], key) -> list[Sighting]:
    """Collapse to one sighting per key, keeping the last in source order (as the original did)."""
    return list({key(s): s for s in sightings}.values())
