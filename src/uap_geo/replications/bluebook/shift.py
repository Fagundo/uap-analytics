"""Did a kind of conclusion become more or less common after a date, nationally and in a region?

The CIA's 1997 history (Haines) says U-2 and OXCART flights accounted for many late-1950s and 1960s reports, and
that Blue Book explained them to the public as natural phenomena. A nationwide change in Blue Book's own rules
would show too. The two predict different things: a rule change is national; a spy-plane effect is regional.

``ShareShiftTest`` measures, for one kind of conclusion (a predicate on index rows), the national change in its
share in the ``window`` months after a date against the ``window`` months before, and the difference in
differences (the change in the region minus the change elsewhere, rows placed in a state). Each is ranked against
the same statistic at every other month in the index (placebo dates).
"""
from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from uap_geo.replications.bluebook.index import IndexRow


def month_index(year: int, month: int) -> int:
    return year * 12 + month - 1


@dataclass
class ShiftResult:
    label: str
    breakpoint: str
    window: int
    national_before: float | None
    national_after: float | None
    national_change: float | None
    national_p: float | None
    region_before: float | None
    region_after: float | None
    rest_before: float | None
    rest_after: float | None
    did: float | None
    did_p: float | None
    counts: dict

    def to_dict(self) -> dict:
        r = lambda v: round(v, 4) if isinstance(v, float) else v
        return {k: r(v) for k, v in self.__dict__.items()}


class ShareShiftTest:
    def __init__(self, rows: list[IndexRow], region: set[str], window: int = 24,
                 placebo_range: tuple[int, int] | None = None):
        self.rows, self.region, self.window = rows, region, window
        ms = [month_index(r.year, r.month) for r in rows]
        lo, hi = placebo_range or (min(ms), max(ms))
        self.placebo = range(lo + window, hi - window + 1)

    def _share(self, rows: Iterable, pred) -> tuple[float | None, int]:
        rows = list(rows)
        return (sum(1 for r in rows if pred(r)) / len(rows), len(rows)) if rows else (None, 0)

    def _span(self, t0: int, rows):
        before = [r for r in rows if t0 - self.window <= month_index(r.year, r.month) < t0]
        after = [r for r in rows if t0 <= month_index(r.year, r.month) < t0 + self.window]
        return before, after

    def _national(self, t0, pred):
        b, a = self._span(t0, self.rows)
        (sb, nb), (sa, na) = self._share(b, pred), self._share(a, pred)
        return (None if sb is None or sa is None else sa - sb), sb, sa, nb, na

    def _did(self, t0, pred):
        placed = [r for r in self.rows if r.state]
        reg = [r for r in placed if r.state in self.region]
        rest = [r for r in placed if r.state not in self.region]
        (rb, ra), (ob, oa) = self._span(t0, reg), self._span(t0, rest)
        vals = [self._share(x, pred) for x in (rb, ra, ob, oa)]
        if any(v[0] is None for v in vals):
            return None, vals
        return (vals[1][0] - vals[0][0]) - (vals[3][0] - vals[2][0]), vals

    @staticmethod
    def _rank(observed, placebo) -> float | None:
        placebo = [p for p in placebo if p is not None]
        if observed is None or not placebo:
            return None
        return (sum(1 for p in placebo if p >= observed - 1e-12) + 1) / (len(placebo) + 1)

    def run(self, label: str, pred: Callable, year: int, month: int) -> ShiftResult:
        t0 = month_index(year, month)
        ch, sb, sa, nb, na = self._national(t0, pred)
        d, vals = self._did(t0, pred)
        return ShiftResult(
            label, f"{year}-{month:02d}", self.window, sb, sa, ch,
            self._rank(ch, (self._national(t, pred)[0] for t in self.placebo)),
            vals[0][0], vals[1][0], vals[2][0], vals[3][0], d,
            self._rank(d, (self._did(t, pred)[0] for t in self.placebo)),
            {"national_before": nb, "national_after": na, "region_before": vals[0][1], "region_after": vals[1][1],
             "rest_before": vals[2][1], "rest_after": vals[3][1]})


PREDICATES: dict[str, Callable] = {
    "aircraft": lambda r: r.category == "aircraft",
    "weather or optical": lambda r: r.family == "weather or optical",
    "aircraft or weather/optical": lambda r: r.category == "aircraft" or r.family == "weather or optical",
    "balloon": lambda r: r.category == "balloon",
    "astro": lambda r: r.category == "astro",
    "unidentified": lambda r: r.category == "unidentified",
    "insufficient data": lambda r: r.category == "insufficient",
}
