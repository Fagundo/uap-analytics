"""One check per kind of explanation. Each asks only what physics and the explanation's own facts allow.

A check never confirms an explanation. It can find that the explanation's stated facts rule it out
(the satellite was already down; the planet was on the other side of the sky), or that nothing it can
measure rules it out.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from uap_analytics.replications.claims import sky
from uap_analytics.replications.claims.model import Case, CheckResult, Claim, Verdict
from uap_analytics.replications.common.geo import (
    angle_diff, bearing_deg, haversine_km, height_for_angle_m, elevation_angle_deg, line_of_sight_km,
)


def _time(value: str) -> datetime:
    t = datetime.fromisoformat(value)
    if t.tzinfo is None:
        raise ValueError(f"time without a timezone: {value!r}")
    return t


class Check(ABC):
    kind = ""

    @abstractmethod
    def run(self, case: Case, claim: Claim) -> CheckResult:
        ...


class BalloonDriftCheck(Check):
    """Could a balloon launched then and there be at the sighting when it was seen?

    event: launch {time, lat, lon}; optional target {time, lat, lon} when the explanation places the
    balloon somewhere other than the case's own place (e.g. where debris was found); optional
    max_speed_kmh (default 200, a strong jet stream), max_hours (flight endurance) and
    stated_bearing {deg, tolerance} for a trajectory the explanation's sources describe.
    """
    kind = "balloon"

    def run(self, case, claim):
        e = claim.event
        launch = e["launch"]
        t0 = _time(launch["time"])
        target = e.get("target") or {}
        t1 = _time(target["time"]) if "time" in target else case.start
        lat1, lon1 = target.get("lat", case.place.lat), target.get("lon", case.place.lon)
        hours = (t1 - t0).total_seconds() / 3600
        km = haversine_km(launch["lat"], launch["lon"], lat1, lon1)
        brg = bearing_deg(launch["lat"], launch["lon"], lat1, lon1)
        m = {"hours_after_launch": round(hours, 2), "distance_km": round(km, 1), "bearing_deg": round(brg, 1),
             "mean_speed_kmh_needed": round(km / hours, 1) if hours > 0 else None}
        out, verdict = [], Verdict.POSSIBLE
        max_speed = e.get("max_speed_kmh", 200)
        if hours <= 0:
            verdict = Verdict.INCONSISTENT
            out.append("The sighting came before the launch.")
        elif km / hours > max_speed:
            verdict = Verdict.INCONSISTENT
            out.append(f"Needs a mean drift of {km / hours:.0f} km/h, above {max_speed} km/h.")
        else:
            out.append(f"Needs a mean drift of {km / hours:.0f} km/h over {hours:.1f} h, within what winds aloft allow.")
            if hours > 72:
                out.append("With this much time between launch and find, timing and distance don't constrain the "
                           "explanation; what is disputed is listed separately.")
        if e.get("max_hours") and hours > e["max_hours"]:
            verdict = Verdict.INCONSISTENT
            out.append(f"{hours:.0f} h after launch is beyond the stated flight endurance of {e['max_hours']} h.")
        sb = e.get("stated_bearing")
        if sb:
            d = angle_diff(brg, sb["deg"])
            m["bearing_off_stated_deg"] = round(d, 1)
            if d > sb.get("tolerance", 45):
                verdict = Verdict.INCONSISTENT
                out.append(f"The sighting lies {d:.0f}° off the trajectory the sources describe.")
            else:
                out.append(f"The sighting lies along the trajectory the sources describe ({d:.0f}° off).")
        return CheckResult(claim, case, verdict, m, out)


class ReentryTimingCheck(Check):
    """A reentering satellite is seen for a minute or two: its reentry time must match the sighting.

    event: time (when it reentered) or before (it had decayed earlier than this), tolerance_min (30);
    plane_crossings: times the case's place passed through the satellite's orbital plane. A satellite
    can only be overhead near those times, so a sighting far from all of them can't be its reentry;
    plane_tolerance_min (60) allows for a reentry seen up to ~1,000 km off the ground track.
    """
    kind = "reentry"

    def run(self, case, claim):
        e = claim.event
        tol = e.get("tolerance_min", 30)
        if e.get("plane_crossings"):
            gaps = [abs((case.start - _time(x)).total_seconds()) / 60 for x in e["plane_crossings"]]
            m = {"minutes_from_nearest_plane_crossing": round(min(gaps), 0)}
            if min(gaps) > e.get("plane_tolerance_min", 60):
                return CheckResult(claim, case, Verdict.INCONSISTENT, m, [
                    f"{case.place.name} passed under the satellite's orbital plane only at "
                    + ", ".join(_time(x).strftime("%H:%M UTC") for x in e["plane_crossings"])
                    + f"; the sighting was {min(gaps) / 60:.1f} h from the nearest, so the satellite couldn't have "
                    "been coming down overhead then."])
        if "time" in e:
            gap = (case.start - _time(e["time"])).total_seconds() / 60
            m = {"minutes_between_reentry_and_sighting": round(gap, 1)}
            if abs(gap) > tol:
                return CheckResult(claim, case, Verdict.INCONSISTENT, m,
                                   [f"Reentry and sighting are {abs(gap):.0f} minutes apart (tolerance {tol})."])
            return CheckResult(claim, case, Verdict.POSSIBLE, m, ["Reentry time matches the sighting."])
        before = _time(e["before"])
        if before <= case.start:
            return CheckResult(claim, case, Verdict.INCONSISTENT, {"decayed_before": before.isoformat()},
                               [f"Tracking places the decay before {before:%H:%M} UTC; the sighting was at "
                                f"{case.start.astimezone(before.tzinfo):%H:%M} UTC or later."])
        return CheckResult(claim, case, Verdict.UNTESTABLE, {}, ["Tracking bound doesn't exclude the sighting time."])


class BolideCheck(Check):
    """A meteor fireball: was it at the right time, and could the case's witnesses have seen it?

    event: time, end {lat, lon, alt_km} (where the luminous flight ended), tolerance_min (15),
    landing_claim_radius_km (50): how far the end point can be from a claimed landing site.
    """
    kind = "bolide"

    def run(self, case, claim):
        e = claim.event
        gap = (case.start - _time(e["time"])).total_seconds() / 60
        end = e["end"]
        km = haversine_km(case.place.lat, case.place.lon, end["lat"], end["lon"])
        sight = line_of_sight_km(end["alt_km"] * 1000, case.place.elevation_m)
        m = {"minutes_apart": round(gap, 1), "end_point_distance_km": round(km, 1),
             "max_visible_distance_km": round(sight, 0)}
        out, verdict = [], Verdict.POSSIBLE
        if abs(gap) > e.get("tolerance_min", 15):
            verdict = Verdict.INCONSISTENT
            out.append(f"Fireball and sighting are {abs(gap):.0f} minutes apart.")
        if km > sight:
            verdict = Verdict.INCONSISTENT
            out.append(f"The end point ({km:.0f} km away) was below the horizon from {case.place.name}.")
        else:
            out.append(f"From {case.place.name} the fireball's end, {km:.0f} km away, was above the horizon "
                       f"(visible to about {sight:.0f} km).")
        if km > e.get("landing_claim_radius_km", 50):
            out.append(f"An object landing at {case.place.name} is not what this trajectory describes: "
                       f"its flight ended {km:.0f} km away.")
        return CheckResult(claim, case, verdict, m, out)


class SkyBodyCheck(Check):
    """Was the planet or star where the witnesses looked, above the horizon, during the sighting?

    event: body (venus | mars | jupiter, or a star in sky.STARS). Uses the case's observation azimuth,
    elevation and side of the Moon (or another body), when the record states them.
    """
    kind = "planet"

    def __init__(self, kind: str = "planet"):
        self.kind = kind

    step_min = 5                                  # the window is sampled this often

    def _times(self, case: Case) -> list[datetime]:
        if case.end <= case.start:
            return [case.start]
        n = max(1, int((case.end - case.start).total_seconds() // (self.step_min * 60)))
        step = (case.end - case.start) / n
        return [case.start + step * k for k in range(n + 1)]

    def run(self, case, claim):
        body = claim.event["body"]
        obs = case.observation
        times = self._times(case)
        pos = [sky.position(body, t, case.place.lat, case.place.lon) for t in times]
        sun = [sky.position("sun", t, case.place.lat, case.place.lon) for t in times]
        ref = ([sky.position(obs.relative_body, t, case.place.lat, case.place.lon) for t in times]
               if obs.relative_body and obs.relative_side else None)
        ends = [0, len(times) - 1] if len(times) > 1 else [0]
        m = {"positions": [{"time": times[i].isoformat(), "azimuth": pos[i].azimuth, "altitude": pos[i].altitude,
                            "sun_altitude": sun[i].altitude} for i in ends],
             "sampled_every_min": self.step_min if len(times) > 1 else None}
        if body not in sky.STARS:
            m["elongation_from_sun_deg"] = sky.elongation(body, times[0])
        up = [i for i, p in enumerate(pos) if p.altitude > 0]
        if not up:
            return CheckResult(claim, case, Verdict.INCONSISTENT, m, [f"{body.title()} was below the horizon."])
        out = [f"{body.title()} was at " + " to ".join(f"azimuth {pos[i].azimuth:.0f}°, altitude {pos[i].altitude:.0f}°"
                                                     for i in ends) + "."]
        if obs.azimuth is None and obs.elevation is None and not (obs.relative_body and obs.relative_side):
            out.append("The record states no direction, elevation or position relative to another body, so the "
                       "position can't be compared.")
            return CheckResult(claim, case, Verdict.UNTESTABLE, m, out)

        def side(i: int) -> str:                  # as the witness faces the reference body: lower azimuth is left
            return "left" if (pos[i].azimuth - ref[i].azimuth + 180) % 360 - 180 < 0 else "right"

        az_off = {i: angle_diff(pos[i].azimuth, obs.azimuth) for i in up} if obs.azimuth is not None else {}
        el_off = {i: abs(pos[i].altitude - obs.elevation) for i in up} if obs.elevation is not None else {}
        ok_az = {i for i in up if obs.azimuth is None or az_off[i] <= obs.azimuth_tolerance}
        ok_el = {i for i in up if obs.elevation is None or el_off[i] <= obs.elevation_tolerance}
        ok_side = {i for i in up if ref is None or side(i) == obs.relative_side}
        joint = ok_az & ok_el & ok_side           # every stated constraint met at the same moment
        verdict = Verdict.POSSIBLE if joint else Verdict.INCONSISTENT
        if az_off:
            best = min(az_off.values())
            m["azimuth_off_report_deg"] = round(best, 1)
            m["azimuth_margin_deg"] = round(obs.azimuth_tolerance - best, 1)
            out.append(f"Closest to the reported direction ({obs.azimuth:.0f}°): {best:.0f}° off "
                       f"(tolerance {obs.azimuth_tolerance:.0f}°).")
        if el_off:
            best = min(el_off.values())
            m["altitude_off_report_deg"] = round(best, 1)
            out.append(f"Closest to the reported elevation ({obs.elevation:.0f}°): {best:.0f}° off "
                       f"(tolerance {obs.elevation_tolerance:.0f}°).")
        if ref is not None:
            sides = {side(i) for i in up}
            m["relative"] = [{"time": times[i].isoformat(), "side": side(i),
                              obs.relative_body: {"azimuth": ref[i].azimuth, "altitude": ref[i].altitude},
                              "azimuth_gap_deg": round((pos[i].azimuth - ref[i].azimuth + 180) % 360 - 180, 1)}
                             for i in ends]
            if obs.relative_side in sides:
                out.append(f"{body.title()} was to the {obs.relative_side} of the {obs.relative_body}, as recorded.")
            else:
                gaps = [abs((pos[i].azimuth - ref[i].azimuth + 180) % 360 - 180) for i in up]
                out.append(f"The record puts the object to the {obs.relative_side} of the {obs.relative_body}; "
                           f"{body.title()} was {min(gaps):.0f}°–{max(gaps):.0f}° to its {sides.pop()} throughout.")
        if verdict is Verdict.INCONSISTENT and (ok_az and ok_el and ok_side):
            out.append("Each constraint is met at some moment, but never all at once.")
        if body not in sky.STARS and any(sun[i].altitude > 0 for i in up):
            out.append(f"Part of the window was daytime (Sun up), {m['elongation_from_sun_deg']:.0f}° from the Sun: "
                       "whether it was bright enough to see is not tested here.")
        return CheckResult(claim, case, verdict, m, out)


class BeaconCheck(Check):
    """A fixed flashing light (lighthouse): direction and flash period against the witnesses' account.

    event: lat, lon, flash_period_s, range_km.
    """
    kind = "beacon"

    def run(self, case, claim):
        e, obs = claim.event, case.observation
        brg = bearing_deg(case.place.lat, case.place.lon, e["lat"], e["lon"])
        km = haversine_km(case.place.lat, case.place.lon, e["lat"], e["lon"])
        m = {"bearing_deg": round(brg, 1), "distance_km": round(km, 1)}
        out, verdict = [], Verdict.POSSIBLE
        if e.get("range_km") and km > e["range_km"]:
            verdict = Verdict.INCONSISTENT
            out.append(f"{km:.0f} km is beyond the light's {e['range_km']} km range.")
        if obs.azimuth is not None:
            d = angle_diff(brg, obs.azimuth)
            m["bearing_off_report_deg"] = round(d, 1)
            if d > obs.azimuth_tolerance:
                verdict = Verdict.INCONSISTENT
                out.append(f"The light is {d:.0f}° from the reported direction.")
            else:
                out.append(f"The light, {km:.1f} km away at {brg:.0f}°, is in the reported direction ({d:.0f}° off).")
        if obs.flash_period_s and e.get("flash_period_s"):
            r = obs.flash_period_s / e["flash_period_s"]
            m["flash_period_ratio"] = round(r, 2)
            if abs(r - 1) > 0.2:
                verdict = Verdict.INCONSISTENT
                out.append(f"Reported flash period {obs.flash_period_s}s vs the light's {e['flash_period_s']}s.")
            else:
                out.append(f"Reported flash period ({obs.flash_period_s}s) matches the light's ({e['flash_period_s']}s).")
        return CheckResult(claim, case, verdict, m, out)


class FlareHorizonCheck(Check):
    """Flares far away: are they in the reported direction, and would they set behind the terrain?

    event: lat, lon (where they were dropped), time, alt_m (drop altitude, if stated);
    obstacle {name, lat, lon, elev_m: [low, high]}: the ridge between the witnesses and the flares.
    """
    kind = "flare"

    def run(self, case, claim):
        e, obs = claim.event, case.observation
        p = case.place
        gap = (case.start - _time(e["time"])).total_seconds() / 60
        km = haversine_km(p.lat, p.lon, e["lat"], e["lon"])
        brg = bearing_deg(p.lat, p.lon, e["lat"], e["lon"])
        m = {"minutes_apart": round(gap, 1), "distance_km": round(km, 1), "bearing_deg": round(brg, 1)}
        out, verdict = [], Verdict.POSSIBLE
        if abs(gap) > e.get("tolerance_min", 30):
            verdict = Verdict.INCONSISTENT
            out.append(f"Flares and sighting are {abs(gap):.0f} minutes apart.")
        if obs.azimuth is not None and angle_diff(brg, obs.azimuth) > obs.azimuth_tolerance:
            verdict = Verdict.INCONSISTENT
            out.append(f"The drop area ({brg:.0f}°) is not in the reported direction ({obs.azimuth:.0f}°).")
        ob = e.get("obstacle")
        if ob:
            okm = haversine_km(p.lat, p.lon, ob["lat"], ob["lon"])
            obrg = bearing_deg(p.lat, p.lon, ob["lat"], ob["lon"])
            m["obstacle"] = {"name": ob["name"], "distance_km": round(okm, 1), "bearing_deg": round(obrg, 1),
                             "bearing_off_flares_deg": round(angle_diff(obrg, brg), 1)}
            needed = []
            for elev in ob["elev_m"]:
                angle = elevation_angle_deg(okm, elev, p.elevation_m)
                needed.append(round(height_for_angle_m(km, angle, p.elevation_m)))
            m["min_flare_altitude_to_be_seen_m"] = needed
            lo, hi = min(needed), max(needed)
            out.append(f"{ob['name']} lies {okm:.0f} km away at {obrg:.0f}°, "
                       f"{angle_diff(obrg, brg):.0f}° from the line to the flares {km:.0f} km away.")
            if angle_diff(obrg, brg) > 10:
                out.append("The ridge point used is off the line of sight; where the ridge crosses that line its "
                           "height may differ, so the altitudes below are indicative.")
            out.append(f"Flares there are visible above the ridge only while higher than about {lo:,}–{hi:,} m "
                       f"({lo * 3.281:,.0f}–{hi * 3.281:,.0f} ft); below that they would vanish behind it.")
            if e.get("alt_m") is not None and e["alt_m"] < lo:
                verdict = Verdict.INCONSISTENT
                out.append(f"The stated drop altitude ({e['alt_m']} m) is too low to be seen at all.")
            elif e.get("alt_m") is None:
                out.append("The drop altitude isn't stated in the sources, so whether they cleared the ridge "
                           "isn't tested.")
        return CheckResult(claim, case, verdict, m, out)


CHECKS: dict[str, Check] = {c.kind: c for c in (
    BalloonDriftCheck(), ReentryTimingCheck(), BolideCheck(), SkyBodyCheck("planet"), SkyBodyCheck("star"),
    BeaconCheck(), FlareHorizonCheck())}


def check(case: Case, claim: Claim) -> CheckResult:
    if claim.kind not in CHECKS:
        raise KeyError(f"no check for kind {claim.kind!r}")
    return CHECKS[claim.kind].run(case, claim)
