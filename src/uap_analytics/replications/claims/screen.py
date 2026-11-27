"""Which bright sky objects could a witness have been looking at? For any place and time.

``SkyScreen.scan`` lists the Sun's altitude (day, twilight or night), the Moon and every bright
planet or star above the horizon. ``SkyScreen.claims_for`` turns that into candidate explanations
for a catalog case, which the ordinary sky check then tests against what the witnesses reported
(direction, elevation, side of the Moon). Candidates come from the sky, not from anyone's claim, so
they are attributed to the screen itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from uap_analytics.replications.claims import sky
from uap_analytics.replications.claims.model import Case, Claim

BODIES = sky.PLANETS + tuple(sky.STAR_MAGNITUDES) + ("moon",)


def twilight(sun_altitude: float) -> str:
    if sun_altitude > 0:
        return "day"
    if sun_altitude > -6:
        return "civil twilight"
    if sun_altitude > -12:
        return "nautical twilight"
    if sun_altitude > -18:
        return "astronomical twilight"
    return "night"


@dataclass(frozen=True)
class Candidate:
    body: str
    magnitude: float
    azimuth: float
    altitude: float

    def to_dict(self) -> dict:
        return {"body": self.body, "magnitude": self.magnitude, "azimuth": self.azimuth, "altitude": self.altitude}


class SkyScreen:
    def __init__(self, bodies: tuple[str, ...] = BODIES, magnitude_limit: float = 1.0, min_altitude: float = 0.0):
        self.bodies, self.limit, self.min_alt = bodies, magnitude_limit, min_altitude

    @staticmethod
    def visible_limit(sun_altitude: float, limit: float) -> float:
        """Faintest magnitude a casual observer could see: in daylight only Venus-class objects and the Moon,
        in civil twilight only the brightest planets and stars, after that the screen's own limit."""
        if sun_altitude > 0:
            return min(limit, -3.5)
        if sun_altitude > -6:
            return min(limit, -1.0)
        return limit

    def candidates(self, t: datetime, lat: float, lon: float) -> list[Candidate]:
        lim = self.visible_limit(sky.position("sun", t, lat, lon).altitude, self.limit)
        out = []
        for b in self.bodies:
            p = sky.position(b, t, lat, lon)
            mag = sky.magnitude(b, t)
            if p.altitude > self.min_alt and mag <= lim:
                out.append(Candidate(b, mag, p.azimuth, p.altitude))
        return sorted(out, key=lambda c: c.magnitude)

    def scan(self, t: datetime, lat: float, lon: float) -> dict:
        sun = sky.position("sun", t, lat, lon)
        moon = sky.position("moon", t, lat, lon)
        return {"time_utc": t.isoformat(), "sun_altitude": sun.altitude, "light": twilight(sun.altitude),
                "moon": {"azimuth": moon.azimuth, "altitude": moon.altitude,
                         "illuminated": sky.illuminated_fraction(t)},
                "candidates": [c.to_dict() for c in self.candidates(t, lat, lon) if c.body != "moon"]}

    def claims_for(self, case: Case) -> list[Claim]:
        """One candidate claim per bright body above the horizon at the start or end of the case."""
        seen: dict[str, None] = {}
        skip = {case.observation.relative_body}               # a body isn't compared with itself
        for t in {case.start, case.end}:
            for c in self.candidates(t, case.place.lat, case.place.lon):
                seen.setdefault(c.body, None)
        return [Claim(id=f"{case.id}-screen-{b}", case_id=case.id, kind="star" if b in sky.STARS else "planet",
                      explanation=f"{b.title()} (bright and above the horizon)", claimed_by="automatic sky screen",
                      event={"body": b}) for b in seen if b not in skip]
