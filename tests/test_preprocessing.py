import pandas as pd
import pytest

from uap_geo.data.preprocessing.geocode import GazetteerGeocoder, normalize_place_name


def _raw(rows):
    return pd.DataFrame(rows, columns=["Occurred", "Location", "Summary"])


def test_geocoder_keeps_source_coordinates_and_fills_gaps():
    gazetteer = pd.DataFrame(
        [["ID", "Boise City city", 43.6, -116.2, 1, "place"], ["AZ", "Phoenix city", 0.0, 0.0, 1, "place"]],
        columns=["state", "name", "lat", "lon", "ALAND", "level"],
    )
    reports = pd.DataFrame(
        {"city": ["Phoenix", "Boise City"], "state": ["AZ", "ID"], "lat": [33.45, None], "lon": [-112.07, None]}
    )
    out = GazetteerGeocoder(gazetteer).geocode(reports)
    assert out.loc[0, "lat"] == 33.45 and out.loc[0, "geocode_level"] == "source"
    assert out.loc[1, "lat"] == 43.6 and out.loc[1, "geocode_level"] == "place"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("St. Louis city", "saint louis"),
        ("Fort Collins city", "fort collins"),
        ("Bethesda CDP", "bethesda"),
        ("Canton charter township", "canton"),
        ("Nashville-Davidson metropolitan government (balance)", "nashville davidson"),
    ],
)
def test_normalize_gazetteer_names(raw, expected):
    assert normalize_place_name(raw, strip_suffix=True) == expected


def test_normalize_report_city_abbreviations():
    assert normalize_place_name("Ft. Collins") == "fort collins"
    assert normalize_place_name("Mt Shasta") == "mount shasta"
    assert normalize_place_name("Westport") == "westport"


def test_geocoder_prefers_place_then_larger_area():
    gazetteer = pd.DataFrame(
        [
            ["MO", "St. Louis city", 38.63, -90.24, 160_000_000, "place"],
            ["MO", "St. Louis township", 1.0, 1.0, 999_000_000, "cousub"],
            ["WA", "Springfield CDP", 47.0, -122.0, 1_000, "place"],
            ["WA", "Springfield city", 47.5, -122.5, 9_000, "place"],
        ],
        columns=["state", "name", "lat", "lon", "ALAND", "level"],
    )
    reports = pd.DataFrame({"city": ["St Louis", "Springfield", "Nowhere"], "state": ["MO", "WA", "WA"]})
    out = GazetteerGeocoder(gazetteer).geocode(reports)
    assert out.loc[0, "lat"] == 38.63 and out.loc[0, "geocode_level"] == "place"
    assert out.loc[1, "lat"] == 47.5
    assert pd.isna(out.loc[2, "lat"])
