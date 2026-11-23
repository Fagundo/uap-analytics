"""Where the Sun, Moon, planets and bright stars were in the sky, to about a degree.

Low-precision orbital elements (Paul Schlyter, "How to compute planetary positions",
https://stjarnhimlen.se/comp/ppcomp.html), good to well under a degree for the Sun, Venus, Mars and
Jupiter between about 1900 and 2100. That is far finer than any witness's "to the southwest", which is
all these checks need. The Moon includes its main perturbations and topocentric parallax; stars are
precessed from J2000 with the low-order formula. No refraction.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone

_RAD = math.pi / 180

# N, i, w, a, e, M as (value at d=0, change per day); d counts days from 1999-12-31 00:00 UT
_ELEMENTS = {
    "sun": ((0.0, 0.0), (0.0, 0.0), (282.9404, 4.70935e-5), (1.0, 0.0), (0.016709, -1.151e-9), (356.0470, 0.9856002585)),
    "venus": ((76.6799, 2.46590e-5), (3.3946, 2.75e-8), (54.8910, 1.38374e-5), (0.723330, 0.0), (0.006773, -1.302e-9),
              (48.0052, 1.6021302244)),
    "mars": ((49.5574, 2.11081e-5), (1.8497, -1.78e-8), (286.5016, 2.92961e-5), (1.523688, 0.0), (0.093405, 2.516e-9),
             (18.6021, 0.5240207766)),
    "saturn": ((113.6634, 2.38980e-5), (2.4886, -1.081e-7), (339.3939, 2.97661e-5), (9.55475, 0.0),
               (0.055546, -9.499e-9), (316.9670, 0.0334442282)),
    "jupiter": ((100.4542, 2.76854e-5), (1.3030, -1.557e-7), (273.8777, 1.64505e-5), (5.20256, 0.0),
                (0.048498, 4.469e-9), (19.8950, 0.0830853001)),
}


def _day(t: datetime) -> float:
    t = t.astimezone(timezone.utc)
    epoch = datetime(1999, 12, 31, tzinfo=timezone.utc)
    return (t - epoch).total_seconds() / 86400.0


def _elements(body: str, d: float) -> tuple[float, ...]:
    return tuple(v0 + dv * d for v0, dv in _ELEMENTS[body])


def _helio(body: str, d: float) -> tuple[float, float, float]:
    """Heliocentric ecliptic rectangular coordinates (AU). For 'sun', the Sun's geocentric position."""
    n, i, w, a, e, m = _elements(body, d)
    m = math.radians(m % 360)
    ea = m + e * math.sin(m) * (1 + e * math.cos(m))
    for _ in range(10):                                  # Kepler's equation
        ea -= (ea - e * math.sin(ea) - m) / (1 - e * math.cos(ea))
    xv, yv = a * (math.cos(ea) - e), a * math.sqrt(1 - e * e) * math.sin(ea)
    v, r = math.atan2(yv, xv), math.hypot(xv, yv)
    n, i, w = math.radians(n), math.radians(i), math.radians(w)
    return (r * (math.cos(n) * math.cos(v + w) - math.sin(n) * math.sin(v + w) * math.cos(i)),
            r * (math.sin(n) * math.cos(v + w) + math.cos(n) * math.sin(v + w) * math.cos(i)),
            r * math.sin(v + w) * math.sin(i))


# J2000 right ascension and declination, degrees (Hipparcos, rounded)
STAR_MAGNITUDES = {"sirius": -1.46, "canopus": -0.74, "arcturus": -0.05, "vega": 0.03, "capella": 0.08}
PLANETS = ("venus", "mars", "jupiter", "saturn")
STARS = {"sirius": (101.2872, -16.7161), "vega": (279.2347, 38.7837), "arcturus": (213.9153, 19.1824),
         "capella": (79.1723, 45.9980), "canopus": (95.9880, -52.6957)}


def _moon_ecliptic(d: float) -> tuple[float, float, float]:
    """Geocentric ecliptic longitude, latitude (degrees) and distance (Earth radii)."""
    n, i, w = 125.1228 - 0.0529538083 * d, 5.1454, 318.0634 + 0.1643573223 * d
    a, e, m = 60.2666, 0.054900, (115.3654 + 13.0649929509 * d) % 360
    mr = math.radians(m)
    ea = mr + e * math.sin(mr) * (1 + e * math.cos(mr))
    for _ in range(10):
        ea -= (ea - e * math.sin(ea) - mr) / (1 - e * math.cos(ea))
    xv, yv = a * (math.cos(ea) - e), a * math.sqrt(1 - e * e) * math.sin(ea)
    v, r = math.atan2(yv, xv), math.hypot(xv, yv)
    nr, ir, wr = math.radians(n), math.radians(i), math.radians(w)
    x = r * (math.cos(nr) * math.cos(v + wr) - math.sin(nr) * math.sin(v + wr) * math.cos(ir))
    y = r * (math.sin(nr) * math.cos(v + wr) + math.cos(nr) * math.sin(v + wr) * math.cos(ir))
    z = r * math.sin(v + wr) * math.sin(ir)
    lon, lat = math.degrees(math.atan2(y, x)), math.degrees(math.atan2(z, math.hypot(x, y)))
    _, _, ws, _, _, ms = _elements("sun", d)
    ls, lm = ms + ws, m + w + n
    dd, f = math.radians(lm - ls), math.radians(lm - n)
    mm, msr = math.radians(m), math.radians(ms)
    lon += (-1.274 * math.sin(mm - 2 * dd) + 0.658 * math.sin(2 * dd) - 0.186 * math.sin(msr)
            - 0.059 * math.sin(2 * mm - 2 * dd) - 0.057 * math.sin(mm - 2 * dd + msr) + 0.053 * math.sin(mm + 2 * dd)
            + 0.046 * math.sin(2 * dd - msr) + 0.041 * math.sin(mm - msr) - 0.035 * math.sin(dd)
            - 0.031 * math.sin(mm + msr) - 0.015 * math.sin(2 * f - 2 * dd) + 0.011 * math.sin(mm - 4 * dd))
    lat += (-0.173 * math.sin(f - 2 * dd) - 0.055 * math.sin(mm - f - 2 * dd) - 0.046 * math.sin(mm + f - 2 * dd)
            + 0.033 * math.sin(f + 2 * dd) + 0.017 * math.sin(2 * mm + f))
    r += -0.58 * math.cos(mm - 2 * dd) - 0.46 * math.cos(2 * dd)
    return lon, lat, r


def _star_radec(name: str, t: datetime) -> tuple[float, float]:
    ra, dec = STARS[name]
    years = _day(t) / 365.25
    dra = (0.012812 + 0.005567 * math.sin(math.radians(ra)) * math.tan(math.radians(dec))) * years
    ddec = 0.005567 * math.cos(math.radians(ra)) * years
    return (ra + dra) % 360, dec + ddec


def ecliptic_geocentric(body: str, t: datetime) -> tuple[float, float, float]:
    d = _day(t)
    sun = _helio("sun", d)
    if body == "sun":
        return sun
    p = _helio(body, d)
    return p[0] + sun[0], p[1] + sun[1], p[2] + sun[2]


def radec(body: str, t: datetime) -> tuple[float, float]:
    """Right ascension and declination, degrees (equinox of date)."""
    if body in STARS:
        return _star_radec(body, t)
    if body == "moon":
        lon, lat, _ = _moon_ecliptic(_day(t))
        lo, la = math.radians(lon), math.radians(lat)
        x, y, z = math.cos(lo) * math.cos(la), math.sin(lo) * math.cos(la), math.sin(la)
    else:
        x, y, z = ecliptic_geocentric(body, t)
    ecl = math.radians(23.4393 - 3.563e-7 * _day(t))
    ye, ze = y * math.cos(ecl) - z * math.sin(ecl), y * math.sin(ecl) + z * math.cos(ecl)
    return math.degrees(math.atan2(ye, x)) % 360, math.degrees(math.atan2(ze, math.hypot(x, ye)))


def sidereal_deg(t: datetime, lon: float) -> float:
    """Local sidereal time in degrees."""
    d = _day(t)
    _, _, w, _, _, m = _elements("sun", d)
    ut = t.astimezone(timezone.utc)
    hours = ut.hour + ut.minute / 60 + ut.second / 3600
    return (w + m + 180 + hours * 15 + lon) % 360


@dataclass(frozen=True)
class SkyPosition:
    body: str
    azimuth: float          # degrees from north, clockwise
    altitude: float         # degrees above the horizon
    ra: float
    dec: float


def position(body: str, t: datetime, lat: float, lon: float) -> SkyPosition:
    ra, dec = radec(body, t)
    ha = math.radians((sidereal_deg(t, lon) - ra) % 360)
    la, de = math.radians(lat), math.radians(dec)
    x, y, z = math.cos(ha) * math.cos(de), math.sin(ha) * math.cos(de), math.sin(de)
    xh = x * math.sin(la) - z * math.cos(la)
    zh = x * math.cos(la) + z * math.sin(la)
    az = (math.degrees(math.atan2(y, xh)) + 180) % 360
    alt = math.degrees(math.asin(max(-1, min(1, zh))))
    if body == "moon":                                   # topocentric parallax lowers the Moon by up to ~1 degree
        alt -= math.degrees(math.asin(1 / _moon_ecliptic(_day(t))[2])) * math.cos(math.radians(alt))
    return SkyPosition(body, round(az, 2), round(alt, 2), round(ra, 3), round(dec, 3))


def separation(ra1: float, dec1: float, ra2: float, dec2: float) -> float:
    """Angle between two directions, degrees."""
    a1, d1, a2, d2 = (math.radians(v) for v in (ra1, dec1, ra2, dec2))
    c = math.sin(d1) * math.sin(d2) + math.cos(d1) * math.cos(d2) * math.cos(a1 - a2)
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def elongation(body: str, t: datetime) -> float:
    """Angle between the body and the Sun as seen from Earth, degrees."""
    return round(separation(*radec(body, t), *radec("sun", t)), 2)


def magnitude(body: str, t: datetime) -> float:
    """Apparent visual magnitude (Schlyter's formulas; Saturn without its rings, so up to ~0.5 too faint)."""
    if body in STAR_MAGNITUDES:
        return STAR_MAGNITUDES[body]
    if body == "moon":                                   # Allen's phase-angle formula; phase angle ~ 180 - elongation
        psi = 180 - elongation("moon", t)
        return round(-12.73 + 0.026 * psi + 4e-9 * psi ** 4, 1)
    d = _day(t)
    h = _helio(body, d)
    sun = _helio("sun", d)
    g = (h[0] + sun[0], h[1] + sun[1], h[2] + sun[2])
    r, big_r, s = math.dist(h, (0, 0, 0)), math.dist(g, (0, 0, 0)), math.dist(sun, (0, 0, 0))
    fv = math.degrees(math.acos(max(-1.0, min(1.0, (r * r + big_r * big_r - s * s) / (2 * r * big_r)))))
    base = {"venus": -4.34 + 0.013 * fv + 4.2e-7 * fv ** 3, "mars": -1.51 + 0.016 * fv,
            "jupiter": -9.25 + 0.014 * fv, "saturn": -9.0 + 0.044 * fv}[body]
    return round(base + 5 * math.log10(r * big_r), 2)


def illuminated_fraction(t: datetime) -> float:
    """Share of the Moon's disc lit, from its elongation."""
    return round((1 - math.cos(math.radians(elongation("moon", t)))) / 2, 3)
