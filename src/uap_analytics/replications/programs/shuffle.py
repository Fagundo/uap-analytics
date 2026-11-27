"""Space-time coincidence tests: do sightings line up with program places *at program times*?

Both tests share one null (a Knox-style space-time interaction test): dates are shuffled among the sightings, so
each place keeps its count of sightings and each date stays in the data, but which place has which date is
random. They differ only in what counts as "at a program's place":

  * ``CoincidenceTest``: the sighting is in one of the program's states.
  * ``ProximityTest``: the sighting's coordinates are within ``radius_km`` of one of the program's sites (only
    sightings with coordinates, only programs with sites).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np

from uap_analytics.replications.common.geo import haversine_km
from uap_analytics.replications.programs.catalog import Program
from uap_analytics.replications.programs.sightings import Sighting


@dataclass
class CoincidenceResult:
    dataset: str
    sightings: int
    observed: int                                 # sightings coinciding with any program
    null_mean: float
    p_value: float                                # share of shuffles with >= observed
    per_program: dict[str, dict] = field(default_factory=dict)
    matches: list[dict] = field(default_factory=list)
    method: str = "state"
    radius_km: float | None = None

    @property
    def ratio(self) -> float | None:
        return round(self.observed / self.null_mean, 2) if self.null_mean else None

    def to_dict(self) -> dict:
        return {"dataset": self.dataset, "method": self.method, "radius_km": self.radius_km,
                "sightings": self.sightings, "observed": self.observed, "null_mean": self.null_mean,
                "ratio": self.ratio, "p_value": self.p_value, "per_program": self.per_program,
                "matches": self.matches}


class ShuffleTest(ABC):
    method = ""

    def __init__(self, programs: list[Program], shuffles: int = 10000, seed: int = 3):
        self.programs, self.shuffles, self.seed = programs, shuffles, seed

    def _programs(self) -> list[Program]:
        return self.programs

    def _eligible(self, sightings: list[Sighting]) -> list[Sighting]:
        return sightings

    @abstractmethod
    def _at_place(self, sightings: list[Sighting], programs: list[Program]):
        """Boolean matrix (sightings x programs): is the sighting at the program's place?"""

    def _result(self, dataset: str, n: int, **kw) -> CoincidenceResult:
        return CoincidenceResult(dataset, n, method=self.method, **kw)

    def run(self, dataset: str, sightings: list[Sighting]) -> CoincidenceResult:
        sightings = self._eligible(sightings)
        programs = self._programs()
        if not sightings or not programs:
            return self._result(dataset, len(sightings), observed=0, null_mean=0.0, p_value=1.0)
        place = np.asarray(self._at_place(sightings, programs), dtype=bool)
        days = np.array([s.date.start.toordinal() for s in sightings])
        lo = np.array([p.start.toordinal() for p in programs])
        hi = np.array([p.end.toordinal() for p in programs])

        def hits(d):
            m = place & (d[:, None] >= lo) & (d[:, None] <= hi)
            return int(m.any(axis=1).sum()), m.sum(axis=0)

        observed, per_obs = hits(days)
        rng = np.random.default_rng(self.seed)
        totals = np.empty(self.shuffles, dtype=int)
        per = np.empty((self.shuffles, len(programs)), dtype=int)
        for k in range(self.shuffles):
            totals[k], per[k] = hits(rng.permutation(days))
        per_program = {p.id: {"name": p.name, "observed": int(per_obs[j]),
                              "null_mean": round(float(per[:, j].mean()), 2),
                              "p_value": round(float((np.sum(per[:, j] >= per_obs[j]) + 1) / (self.shuffles + 1)), 4)}
                       for j, p in enumerate(programs)}
        on = place & (days[:, None] >= lo) & (days[:, None] <= hi)
        matches = [{"id": s.id, "date": s.date.iso, "state": s.state, "group": s.group,
                    "programs": [programs[j].id for j in np.where(on[i])[0]]}
                   for i, s in enumerate(sightings) if on[i].any()]
        return self._result(dataset, len(sightings), observed=observed, null_mean=round(float(totals.mean()), 2),
                            p_value=round(float((np.sum(totals >= observed) + 1) / (self.shuffles + 1)), 4),
                            per_program=per_program, matches=matches)


class CoincidenceTest(ShuffleTest):
    method = "state"

    def _at_place(self, sightings, programs):
        return [[s.state in p.states for p in programs] for s in sightings]


class ProximityTest(ShuffleTest):
    method = "distance"

    def __init__(self, programs: list[Program], radius_km: float = 300.0, shuffles: int = 10000, seed: int = 3):
        super().__init__(programs, shuffles, seed)
        self.radius_km = radius_km

    def _programs(self):
        return [p for p in self.programs if p.sites]

    def _eligible(self, sightings):
        return [s for s in sightings if s.lat is not None and s.lon is not None]

    def _at_place(self, sightings, programs):
        return [[any(haversine_km(s.lat, s.lon, x.lat, x.lon) <= self.radius_km for x in p.sites) for p in programs]
                for s in sightings]

    def _result(self, dataset, n, **kw):
        return CoincidenceResult(dataset, n, method=self.method, radius_km=self.radius_km, **kw)
