"""Flight programs: when and where each flew."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Site:
    name: str
    lat: float
    lon: float


@dataclass(frozen=True)
class Program:
    id: str
    name: str
    kind: str
    start: date                                   # first day of the program's window
    end: date                                     # last day
    states: frozenset[str]                        # state names
    sites: tuple[Site, ...] = ()                  # launch or operating sites with verified coordinates

    def active(self, day: date) -> bool:
        return self.start <= day <= self.end

    def covers(self, state: str, day: date) -> bool:
        return state in self.states and self.active(day)
