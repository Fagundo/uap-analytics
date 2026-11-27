"""Do reports rise in the days after an event (a nuclear test)?

Observed: sightings dated within ``window_days`` after any event (day 0 = the event's day), optionally only those
within ``radius_km`` of the event site. Null: events are grouped into series (consecutive events no more than
``block_gap_days`` apart), and each series is moved as a block by a random whole number of days within
+/- ``jitter_days``, which keeps the season and the spacing inside each series. The statistic is reports per
covered day (days inside any window), because moving events changes how many days they cover. The p-value is
the share of shifted runs whose rate is at least the observed rate; ``null_mean`` is the expected count at the
null rate over the observed covered days. Only day-precise sightings are used.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

import numpy as np

from uap_analytics.replications.common.dates import Precision
from uap_analytics.replications.common.geo import haversine_km
from uap_analytics.replications.programs.sightings import Sighting


@dataclass(frozen=True)
class SiteEvent:
    day: date
    lat: float
    lon: float
    label: str = ""


@dataclass
class WindowResult:
    dataset: str
    events: str
    sightings: int                                # day-precise sightings considered
    window_days: int
    radius_km: float | None
    covered_days: int
    covered_days_null: float
    observed: int
    null_mean: float
    p_value: float
    top_days: list[dict] = field(default_factory=list)

    @property
    def ratio(self) -> float | None:
        return round(self.observed / self.null_mean, 2) if self.null_mean else None

    def to_dict(self) -> dict:
        return {"dataset": self.dataset, "events": self.events, "sightings": self.sightings,
                "window_days": self.window_days, "radius_km": self.radius_km, "covered_days": self.covered_days,
                "covered_days_null": self.covered_days_null, "observed": self.observed,
                "null_mean": self.null_mean, "ratio": self.ratio, "p_value": self.p_value, "top_days": self.top_days}


class EventWindowTest:
    def __init__(self, window_days: int = 2, radius_km: float | None = None, jitter_days: int = 30,
                 shuffles: int = 5000, seed: int = 9, block_gap_days: int = 7,
                 center: tuple[float, float] | None = None):
        self.window, self.radius, self.jitter, self.shuffles, self.seed = window_days, radius_km, jitter_days, shuffles, seed
        self.block_gap = block_gap_days
        self.center = center                      # distance is measured from here when given (a test site)

    def _blocks(self, ev) -> list[int]:
        labels, current = [0], 0
        for a, b in zip(ev[:-1], ev[1:]):
            current += int(b - a > self.block_gap)
            labels.append(current)
        return labels

    def run(self, dataset: str, events_label: str, events: list[SiteEvent], sightings: list[Sighting]) -> WindowResult:
        days = [s for s in sightings if s.date.precision == Precision.DAY]
        if self.radius is not None:
            points = [self.center] if self.center else sorted({(round(e.lat, 2), round(e.lon, 2)) for e in events})
            days = [s for s in days if s.lat is not None
                    and min(haversine_km(s.lat, s.lon, a, b) for a, b in points) <= self.radius]
        if not events or not days:
            return WindowResult(dataset, events_label, len(days), self.window, self.radius, 0, 0.0, 0, 0.0, 1.0)
        base = min(min(s.date.start for s in days), min(e.day for e in events)).toordinal() - self.jitter - 1
        span = max(max(s.date.start for s in days), max(e.day for e in events)).toordinal() - base + self.jitter + self.window + 2
        per_day = np.bincount([s.date.start.toordinal() - base for s in days], minlength=span)
        ev = np.sort(np.array([e.day.toordinal() - base for e in events]))
        blocks = np.array(self._blocks(ev))
        n_blocks = int(blocks.max()) + 1
        offsets = np.arange(self.window + 1)

        def count(starts) -> tuple[int, int]:
            covered = np.zeros(span, dtype=bool)
            covered[(starts[:, None] + offsets).ravel()] = True
            return int(per_day[covered].sum()), int(covered.sum())

        observed, cov = count(ev)
        rng = np.random.default_rng(self.seed)
        runs = [count(ev + rng.integers(-self.jitter, self.jitter + 1, size=n_blocks)[blocks])
                for _ in range(self.shuffles)]
        rates = np.array([r[0] / r[1] for r in runs])
        cov_null = float(np.mean([r[1] for r in runs]))
        rate = observed / cov
        covered = sorted({int(d) for d in (ev[:, None] + offsets).ravel()})
        top = sorted(((int(per_day[d]), d) for d in covered if per_day[d]), reverse=True)[:5]
        top_days = [{"date": date.fromordinal(d + base).isoformat(), "reports": n} for n, d in top]
        return WindowResult(dataset, events_label, len(days), self.window, self.radius, cov, round(cov_null, 1),
                            observed, round(float(rates.mean() * cov), 2),
                            round(float((np.sum(rates >= rate - 1e-12) + 1) / (self.shuffles + 1)), 4), top_days)
