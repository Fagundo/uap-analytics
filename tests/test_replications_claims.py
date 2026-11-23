"""Claims replication: the explanation checks and sky positions (ported unchanged with the code)."""
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from uap_geo.replications.claims.checks import check
from uap_geo.replications.claims.model import Case, Claim, Observation, Place, Verdict
from uap_geo.replications.claims.report import find_incidents
from uap_geo.replications.claims.sky import elongation, position, radec
from uap_geo.replications.common.geo import bearing_deg, elevation_angle_deg, height_for_angle_m, line_of_sight_km

UTC = timezone.utc
T = datetime(1960, 6, 1, 12, 0, tzinfo=UTC)


def case(obs=Observation(), lat=40.0, lon=-100.0, start=T, end=None, elev=0.0, terms=()):
    return Case("c", "Case", start, end or start, Place("Here", lat, lon, elev), obs, place_terms=terms)


def claim(kind, event):
    return Claim("k", "c", kind, "x", "someone", event)


class SkyTest(unittest.TestCase):
    def test_known_events(self):
        ra, dec = radec("sun", datetime(2020, 3, 20, 3, 50, tzinfo=UTC))
        self.assertLess(abs(dec), 0.1)
        self.assertAlmostEqual(elongation("venus", datetime(2020, 3, 24, tzinfo=UTC)), 46.1, delta=0.5)
        self.assertLess(elongation("venus", datetime(2020, 6, 3, 18, tzinfo=UTC)), 1.5)
        self.assertGreater(elongation("jupiter", datetime(2020, 7, 14, 8, tzinfo=UTC)), 178)

    def test_moon_and_stars(self):
        self.assertGreater(elongation("moon", datetime(2020, 10, 31, 14, 49, tzinfo=UTC)), 174)   # full moon
        self.assertLess(elongation("moon", datetime(2020, 11, 15, 5, 7, tzinfo=UTC)), 5)          # new moon
        t = datetime(2017, 8, 21, 18, 26, tzinfo=UTC)                                           # total eclipse, KY
        m, s = position("moon", t, 36.97, -87.67), position("sun", t, 36.97, -87.67)
        self.assertLess(abs(m.azimuth - s.azimuth) + abs(m.altitude - s.altitude), 1.0)
        ra, dec = radec("sirius", datetime(2020, 1, 1, tzinfo=UTC))
        self.assertAlmostEqual(ra, 101.5, delta=0.1)
        self.assertAlmostEqual(dec, -16.74, delta=0.05)

    def test_noon_sun_due_south(self):
        p = position("sun", datetime(2020, 6, 21, 12, 2, tzinfo=UTC), 51.48, 0.0)
        self.assertAlmostEqual(p.azimuth, 180, delta=1)
        self.assertAlmostEqual(p.altitude, 61.96, delta=0.5)


class GeoTest(unittest.TestCase):
    def test_bearing_and_sight(self):
        self.assertAlmostEqual(bearing_deg(0, 0, 0, 1), 90, delta=0.01)
        self.assertAlmostEqual(line_of_sight_km(20000), 545, delta=15)
        a = elevation_angle_deg(80, 3000, 300)
        self.assertAlmostEqual(height_for_angle_m(80, a, 300), 3000, delta=1)


class ChecksTest(unittest.TestCase):
    def test_balloon(self):
        launch = {"time": (T - timedelta(hours=10)).isoformat(), "lat": 40.0, "lon": -101.0}
        self.assertEqual(check(case(), claim("balloon", {"launch": launch})).verdict, Verdict.POSSIBLE)
        late = {**launch, "time": (T + timedelta(hours=1)).isoformat()}
        self.assertEqual(check(case(), claim("balloon", {"launch": late})).verdict, Verdict.INCONSISTENT)
        fast = {**launch, "time": (T - timedelta(minutes=10)).isoformat()}
        self.assertEqual(check(case(), claim("balloon", {"launch": fast})).verdict, Verdict.INCONSISTENT)
        wrong_way = {"launch": launch, "stated_bearing": {"deg": 270, "tolerance": 45}}   # sighting is east of launch
        self.assertEqual(check(case(), claim("balloon", wrong_way)).verdict, Verdict.INCONSISTENT)

    def test_reentry_orbital_plane(self):
        far = {"plane_crossings": [(T - timedelta(hours=6)).isoformat(), (T + timedelta(hours=6)).isoformat()]}
        self.assertEqual(check(case(), claim("reentry", far)).verdict, Verdict.INCONSISTENT)
        near = {"plane_crossings": [(T - timedelta(minutes=20)).isoformat()], "time": T.isoformat()}
        self.assertEqual(check(case(), claim("reentry", near)).verdict, Verdict.POSSIBLE)

    def test_reentry(self):
        self.assertEqual(check(case(), claim("reentry", {"before": T.isoformat()})).verdict, Verdict.INCONSISTENT)
        on_time = {"time": (T - timedelta(minutes=5)).isoformat()}
        self.assertEqual(check(case(), claim("reentry", on_time)).verdict, Verdict.POSSIBLE)

    def test_bolide_out_of_sight(self):
        far = {"time": T.isoformat(), "end": {"lat": 40.0, "lon": -80.0, "alt_km": 20}}
        r = check(case(), claim("bolide", far))
        self.assertEqual(r.verdict, Verdict.INCONSISTENT)

    def test_planet_direction(self):
        venus = position("venus", T, 40.0, -100.0)
        ok = case(Observation(azimuth=venus.azimuth, azimuth_tolerance=10))
        self.assertEqual(check(ok, claim("planet", {"body": "venus"})).verdict, Verdict.POSSIBLE)
        opposite = case(Observation(azimuth=(venus.azimuth + 180) % 360, azimuth_tolerance=10))
        self.assertEqual(check(opposite, claim("planet", {"body": "venus"})).verdict, Verdict.INCONSISTENT)

    def test_side_of_moon(self):
        t = datetime(1966, 4, 17, 11, 0, tzinfo=UTC)
        venus, moon = position("venus", t, 40.66, -80.24), position("moon", t, 40.66, -80.24)
        actual = "left" if (venus.azimuth - moon.azimuth + 180) % 360 - 180 < 0 else "right"
        wrong = "right" if actual == "left" else "left"
        mk = lambda side: case(Observation(relative_body="moon", relative_side=side), lat=40.66, lon=-80.24, start=t)
        self.assertEqual(check(mk(actual), claim("planet", {"body": "venus"})).verdict, Verdict.POSSIBLE)
        self.assertEqual(check(mk(wrong), claim("planet", {"body": "venus"})).verdict, Verdict.INCONSISTENT)

    def test_window_is_sampled_not_just_endpoints(self):
        start, end = datetime(1986, 11, 18, 2, 11, tzinfo=UTC), datetime(1986, 11, 18, 3, 53, tzinfo=UTC)
        a0 = position("jupiter", start, 66.57, -145.26).azimuth
        a1 = position("jupiter", end, 66.57, -145.26).azimuth
        mid = (a0 + a1) / 2                                 # Jupiter crosses this azimuth mid-window
        tol = (a1 - a0) / 2 - 3                             # both endpoints are outside the tolerance
        c = case(Observation(azimuth=mid, azimuth_tolerance=tol), lat=66.57, lon=-145.26, start=start, end=end)
        self.assertEqual(check(c, claim("planet", {"body": "jupiter"})).verdict, Verdict.POSSIBLE)

    def test_constraints_must_hold_at_the_same_moment(self):
        start, end = datetime(1948, 1, 7, 19, 45, tzinfo=UTC), datetime(1948, 1, 7, 21, 15, tzinfo=UTC)
        first = position("venus", start, 37.9, -86.0)
        last = position("venus", end, 37.9, -86.0)
        obs = Observation(azimuth=first.azimuth, azimuth_tolerance=3, elevation=last.altitude, elevation_tolerance=0.3)
        r = check(case(obs, lat=37.9, lon=-86.0, start=start, end=end), claim("planet", {"body": "venus"}))
        self.assertEqual(r.verdict, Verdict.INCONSISTENT)
        self.assertIn("never all at once", " ".join(r.findings))

    def test_star(self):
        r = check(case(start=datetime(1968, 10, 24, 9, 0, tzinfo=UTC), lat=48.6, lon=-101.7),
                  claim("star", {"body": "sirius"}))
        self.assertNotIn("elongation_from_sun_deg", r.metrics)

    def test_beacon_period(self):
        light = {"lat": 40.0, "lon": -99.9, "flash_period_s": 5}
        self.assertEqual(check(case(Observation(azimuth=90, flash_period_s=5)), claim("beacon", light)).verdict,
                         Verdict.POSSIBLE)
        self.assertEqual(check(case(Observation(azimuth=90, flash_period_s=15)), claim("beacon", light)).verdict,
                         Verdict.INCONSISTENT)

    def test_flare_behind_ridge(self):
        ev = {"time": T.isoformat(), "lat": 39.3, "lon": -100.0,
              "obstacle": {"name": "Ridge", "lat": 39.75, "lon": -100.0, "elev_m": [1200]}}
        r = check(case(elev=300), claim("flare", ev))
        self.assertEqual(r.verdict, Verdict.POSSIBLE)
        need = r.metrics["min_flare_altitude_to_be_seen_m"][0]
        self.assertGreater(need, 1200)
        low = check(case(elev=300), claim("flare", {**ev, "alt_m": need - 500}))
        self.assertEqual(low.verdict, Verdict.INCONSISTENT)


class IncidentMatchTest(unittest.TestCase):
    def test_find_incidents(self):
        c = case(terms=("godman",), start=datetime(1948, 1, 7, 19, 45, tzinfo=UTC))
        hit = SimpleNamespace(date="1948-01-07", location_text="Godman Field, Ky.", summary="")
        other_day = SimpleNamespace(date="1948-03-01", location_text="Godman Field", summary="")
        other_place = SimpleNamespace(date="1948-01-07", location_text="Ohio", summary="")
        self.assertEqual(find_incidents(c, [hit, other_day, other_place]), [hit])


if __name__ == "__main__":
    unittest.main()
