"""Cases, the explanations offered for them, and what a check found."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


@dataclass(frozen=True)
class Place:
    name: str
    lat: float
    lon: float
    elevation_m: float = 0.0
    note: str = ""                                # how the coordinates were obtained, when not a direct source


@dataclass(frozen=True)
class Observation:
    """What witnesses reported about direction and timing, when the record states it."""
    azimuth: float | None = None                  # compass degrees
    azimuth_tolerance: float = 30.0               # how loosely the record states it
    elevation: float | None = None
    elevation_tolerance: float = 30.0
    flash_period_s: float | None = None
    relative_body: str | None = None              # e.g. 'moon' when the record places the object beside it
    relative_side: str | None = None              # 'left' | 'right' of that body, as the witness faced it
    note: str = ""


@dataclass(frozen=True)
class Case:
    id: str
    name: str
    start: datetime                               # when the sighting began (timezone-aware)
    end: datetime                                 # when it ended (same as start if a moment)
    place: Place
    observation: Observation = Observation()
    place_terms: tuple[str, ...] = ()             # words that identify the case in PURSUE incident locations
    match_days: int = 5                           # how far from the case date a PURSUE incident may be
    sources: tuple[str, ...] = ()


@dataclass(frozen=True)
class Claim:
    id: str
    case_id: str
    kind: str                                     # balloon | reentry | bolide | planet | star | beacon | flare
    explanation: str
    claimed_by: str                               # who offered it, and when
    event: dict                                   # the explanation's own facts (times, places), per kind
    sources: tuple[str, ...] = ()
    disputes: tuple[str, ...] = ()                # facts the explanation depends on that are contested


class Verdict(str, Enum):
    INCONSISTENT = "inconsistent"                 # the explanation's own stated facts rule it out
    POSSIBLE = "possible"                         # passes every check that could be run; not a confirmation
    UNTESTABLE = "not testable here"


@dataclass
class CheckResult:
    claim: Claim
    case: Case
    verdict: Verdict
    metrics: dict = field(default_factory=dict)
    findings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"claim": self.claim.id, "case": self.case.id, "case_name": self.case.name, "kind": self.claim.kind,
                "explanation": self.claim.explanation, "claimed_by": self.claim.claimed_by,
                "verdict": self.verdict.value, "metrics": self.metrics, "findings": self.findings,
                "disputes": list(self.claim.disputes), "sources": list(self.claim.sources)}
