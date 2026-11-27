"""What uap-analytics still computes itself about single reports: removing NUFORC's notes from the text (the input
to blinded LLM extraction) and the launch-window match, which the LLM gate uses with its own settings
(twilight launches only) to form a comparison group.

The residual set's explanation flags (rules and checks) come from uap-data's export since the data refactor
(Phase 3b-4): uap-data reproduces residual set v2 report for report (its scripts/residual_parity.py)."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from uap_analytics.data.preprocessing.mainshocks import haversine_km
from uap_analytics.events.sun import lighting_class, solar_altitude

NOTE = re.compile(r"\(\(.*?\)\)", re.DOTALL)   # non-greedy: notes can hold their own parentheses, e.g. "(EDT)"


def strip_notes(text: pd.Series) -> pd.Series:
    """Remove NUFORC's ((...)) notes, which name explanations and would leak them to a reader."""
    return text.astype("string").fillna("").str.replace(NOTE, "", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()


class Check(ABC):
    name: str = ""

    def __init__(self, params: dict) -> None:
        self.params = params
        self.confidence = params.get("confidence", "possible")

    @abstractmethod
    def match(self, reports: pd.DataFrame) -> pd.Series:
        """reports: occurred_utc, local_time, lat, lon, duration_s, text (lower-case, notes stripped)."""


class LaunchWindowCheck(Check):
    """Report within N minutes after a twilight or night launch, within the radius of the pad."""

    name = "launch_window"

    def __init__(self, params: dict, launches: pd.DataFrame) -> None:
        super().__init__(params)
        alt = solar_altitude(launches["time_utc"], launches["lat"].to_numpy(), launches["lon"].to_numpy())
        light = lighting_class(alt, tuple(params["twilight_sun_alt"]))
        self.launches = launches.loc[np.isin(light, params["lighting"])].reset_index(drop=True)

    def match(self, reports: pd.DataFrame) -> pd.Series:
        out = np.zeros(len(reports), bool)
        order = np.argsort(reports["occurred_utc"].to_numpy())
        times = reports["occurred_utc"].to_numpy()[order]
        lat, lon = reports["lat"].to_numpy()[order], reports["lon"].to_numpy()[order]
        window = np.timedelta64(int(self.params["minutes_after"]), "m")
        for row in self.launches.itertuples():
            start = np.datetime64(row.time_utc)
            lo, hi = np.searchsorted(times, start), np.searchsorted(times, start + window)
            if hi > lo:
                near = haversine_km(row.lat, row.lon, lat[lo:hi], lon[lo:hi]) <= self.params["radius_km"]
                out[order[lo:hi][near]] = True
        return pd.Series(out, index=reports.index)
