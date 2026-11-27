"""Partial dates as the documents state them (the data repository's parser, kept as it was for the replications).

Extracted dates come in many shapes: ``1952-10-14``, ``1947-11``, ``1948``, ``14 Oct 1952``, ``18 Apr``
(no year), ``1964-11-18/1964-11-24`` (a range), ``1949-03-06/07``. ``PartialDate`` keeps only what the
text actually states, as an inclusive day interval plus the precision it was stated at, so two dates
can be compared without inventing a missing month or year.

Two dates *conflict* when their intervals are further apart than a tolerance. They *agree* when both
are stated to the day and fall within the tolerance. Anything coarser is merely *compatible*.
"""
from __future__ import annotations

import calendar
import re
from dataclasses import dataclass
from datetime import date
from enum import IntEnum

_MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_abbr) if m}
_MONTHS.update({m.lower(): i for i, m in enumerate(calendar.month_name) if m})
_MONTHS["sept"] = 9

_ISO = re.compile(r"^(\d{4})(?:-(\d{1,2}|\?)(?:-(\d{1,2}|\?))?)?$")
_DECADE = re.compile(r"^(1[5-9]\d|20\d)0s$")                                  # 1950s
_SEASON_FIRST = re.compile(r"^(spring|summer|fall|autumn|winter)\s+(\d{4})$")  # Summer 2006
_SEASON_LAST = re.compile(r"^(\d{4})-(spring|summer|fall|autumn|winter)$")     # 1995-summer
_YEAR_SPAN = re.compile(r"^(\d{4})-(\d{4})$")                                  # 1943-1944
# Two stated dates joined by words ("2003 to 2010", "1966 or 1967", "2022 and 2023"): the interval
# covering both. A slash range is handled separately.
_JOINED = re.compile(r"^(.+?)\s+(?:to|through|or|and|-)\s+(.+)$")
# Northern-hemisphere meteorological seasons; winter starts in December of the stated year.
_SEASONS = {"spring": (3, 5), "summer": (6, 8), "fall": (9, 11), "autumn": (9, 11), "winter": (12, 14)}
_DMY = re.compile(r"^(\d{1,2})\s+([a-z]+)\.?,?(?:\s+(\d{4}))?$")
_MDY = re.compile(r"^([a-z]+)\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?(?:\s+(\d{4}))?$")
_MY = re.compile(r"^([a-z]+)\.?,?\s+(\d{4})$")
_SHORT_RANGE = re.compile(r"^(\d{4}-\d{1,2}-)(\d{1,2})/(\d{1,2})$")      # 1949-03-06/07


class Precision(IntEnum):
    YEAR = 1
    MONTH = 2
    DAY = 3


@dataclass(frozen=True)
class PartialDate:
    start: date
    end: date
    precision: Precision          # the coarsest part stated (a day range is still DAY)

    # ------------------------------------------------------------------ parsing
    @classmethod
    def parse(cls, text: str | None) -> PartialDate | None:
        """``None`` when no year is stated: a bare "18 Apr" cannot be placed on a timeline."""
        if not text:
            return None
        s = text.strip().lower()
        m = _SHORT_RANGE.match(s)
        if m:
            s = f"{m[1]}{m[2]}/{m[1]}{m[3]}"
        if "/" in s:
            return cls._span(*(p.strip() for p in s.split("/", 1)))
        one = cls._parse_one(s)
        if one is not None:
            return one
        m = _YEAR_SPAN.match(s)
        if m:
            return cls._span(m[1], m[2])
        m = _JOINED.match(s)
        if m:
            return cls._span(m[1], m[2])
        return None

    @classmethod
    def _span(cls, a_text: str, b_text: str) -> PartialDate | None:
        """The interval covering two stated dates, at the coarser precision; ``None`` if either fails."""
        a, b = cls._parse_one(a_text), cls._parse_one(b_text)
        if a is None or b is None:
            return None
        lo, hi = (a, b) if a.start <= b.start else (b, a)
        return cls(lo.start, max(a.end, b.end), min(a.precision, b.precision))

    @classmethod
    def _parse_one(cls, s: str) -> PartialDate | None:
        try:
            m = _ISO.match(s)
            if m:
                y = int(m[1])
                if m[2] in (None, "?"):
                    return cls._year(y)
                if m[3] in (None, "?"):                  # "1950-04-?": the month is stated
                    return cls._month(y, int(m[2]))
                return cls._day(y, int(m[2]), int(m[3]))
            m = _DECADE.match(s)
            if m:
                y = int(m[1]) * 10
                return cls(date(y, 1, 1), date(y + 9, 12, 31), Precision.YEAR)
            m = _SEASON_FIRST.match(s) or _SEASON_LAST.match(s)
            if m:
                season, y = (m[1], int(m[2])) if m[1].isalpha() else (m[2], int(m[1]))
                return cls._months(y, *_SEASONS[season])
            m = _DMY.match(s)
            if m and m[3] and m[2] in _MONTHS:
                return cls._day(int(m[3]), _MONTHS[m[2]], int(m[1]))
            m = _MDY.match(s)
            if m and m[3] and m[1] in _MONTHS:
                return cls._day(int(m[3]), _MONTHS[m[1]], int(m[2]))
            m = _MY.match(s)
            if m and m[1] in _MONTHS:
                return cls._month(int(m[2]), _MONTHS[m[1]])
        except ValueError:                       # "1953-02-30" and similar OCR damage
            return None
        return None

    @classmethod
    def _year(cls, y: int) -> PartialDate:
        return cls(date(y, 1, 1), date(y, 12, 31), Precision.YEAR)

    @classmethod
    def _month(cls, y: int, mo: int) -> PartialDate:
        return cls(date(y, mo, 1), date(y, mo, calendar.monthrange(y, mo)[1]), Precision.MONTH)

    @classmethod
    def _months(cls, y: int, first: int, last: int) -> PartialDate:
        """Months ``first``..``last`` of year ``y``; ``last`` past 12 runs into the next year."""
        end_y, end_m = y + (last - 1) // 12, (last - 1) % 12 + 1
        return cls(date(y, first, 1), date(end_y, end_m, calendar.monthrange(end_y, end_m)[1]),
                   Precision.MONTH)

    @classmethod
    def _day(cls, y: int, mo: int, d: int) -> PartialDate:
        day = date(y, mo, d)
        return cls(day, day, Precision.DAY)

    # --------------------------------------------------------------- comparison
    def gap_days(self, other: PartialDate) -> int:
        """Days between the two intervals; 0 when they overlap."""
        if self.end < other.start:
            return (other.start - self.end).days
        if other.end < self.start:
            return (self.start - other.end).days
        return 0

    def conflicts(self, other: PartialDate, tolerance_days: int) -> bool:
        return self.gap_days(other) > tolerance_days

    def agrees(self, other: PartialDate, tolerance_days: int) -> bool:
        """Both stated to the day and within the tolerance (allows typed-up date slips)."""
        return (self.precision == other.precision == Precision.DAY
                and self.gap_days(other) <= tolerance_days)

    @property
    def iso(self) -> str:
        if self.precision == Precision.YEAR and self.start.year == self.end.year:
            return f"{self.start.year}"
        if self.precision == Precision.MONTH and self.start.month == self.end.month:
            return self.start.strftime("%Y-%m")
        if self.start == self.end:
            return self.start.isoformat()
        # Write a range at its stated precision, so it parses back the same: "1950/1959", not
        # "1950-01-01/1959-12-31", which would read as two dates stated to the day.
        if self.precision == Precision.YEAR:
            return f"{self.start.year}/{self.end.year}"
        if self.precision == Precision.MONTH:
            return f"{self.start.strftime('%Y-%m')}/{self.end.strftime('%Y-%m')}"
        return f"{self.start.isoformat()}/{self.end.isoformat()}"
