"""A report's date as the export states it: the first and last day it could refer to, and how precise it is."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import IntEnum


class Precision(IntEnum):
    YEAR = 1
    MONTH = 2
    DAY = 3

    @classmethod
    def parse(cls, text: str) -> Precision:
        return cls[text.upper()]


@dataclass(frozen=True)
class Span:
    start: date
    end: date
    precision: Precision

    @property
    def iso(self) -> str:
        if self.precision == Precision.DAY:
            return self.start.isoformat()
        if self.precision == Precision.MONTH:
            return self.start.isoformat()[:7]
        return str(self.start.year)
