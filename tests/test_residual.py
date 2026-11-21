import pandas as pd

from uap_geo.residual.checks import LaunchWindowCheck, strip_notes


def _reports(rows):
    df = pd.DataFrame(rows, columns=["occurred_utc", "local_time", "lat", "lon", "duration_s", "text"])
    df["occurred_utc"] = pd.to_datetime(df["occurred_utc"])
    df["local_time"] = pd.to_datetime(df["local_time"])
    return df


def test_strip_notes():
    s = pd.Series(["Bright orb ((NUFORC Note: Venus. PD)) over hills", "plain",
                   "((NUFORC Note: Missile launch at 2055 hrs (EDT). PD)) bright object exploded"])
    assert strip_notes(s).tolist() == ["Bright orb over hills", "plain", "bright object exploded"]


def test_launch_window_uses_time_and_distance():
    launches = pd.DataFrame({"time_utc": [pd.Timestamp("2017-12-23 01:27")], "lat": [34.7], "lon": [-120.6]})
    check = LaunchWindowCheck({"minutes_after": 90, "radius_km": 1200, "lighting": ["twilight", "night"],
                               "twilight_sun_alt": [-18, -4]}, launches)
    r = _reports([["2017-12-23 01:40", "2017-12-22 17:40", 33.4, -112.0, 300, "spiral"],     # Phoenix, in window
                  ["2017-12-23 03:30", "2017-12-22 19:30", 33.4, -112.0, 300, "spiral"],     # too late
                  ["2017-12-23 01:40", "2017-12-22 20:40", 40.7, -74.0, 300, "spiral"]])     # New York, too far
    assert check.match(r).tolist() == [True, False, False]




def test_reasons_from_pursue_labels():
    import pytest
    pytest.importorskip("geopandas")
    from uap_geo.residual.builder import ResidualSetBuilder
    labels = ["rule:aircraft_helicopter:medium", "rule:meteor_fireball:high", "rule:nuforc_note:high",
              "check:holiday_night:possible", "check:starlink_train:high"]
    assert ResidualSetBuilder.reasons(labels) == ["meteor_fireball", "holiday_night", "starlink_train"]
    assert ResidualSetBuilder.reasons(["rule:drone:medium"]) == []


def test_reasons_from_pursue_labels():
    import pytest
    pytest.importorskip("geopandas")
    from uap_geo.residual.builder import ResidualSetBuilder
    labels = ["rule:aircraft_helicopter:medium", "rule:meteor_fireball:high", "rule:nuforc_note:high",
              "check:holiday_night:possible", "check:starlink_train:high"]
    assert ResidualSetBuilder.reasons(labels) == ["meteor_fireball", "holiday_night", "starlink_train"]
    assert ResidualSetBuilder.reasons(["rule:drone:medium"]) == []
