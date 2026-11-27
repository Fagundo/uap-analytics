import json
import math

import pandas as pd

from uap_analytics.common.geo import COUNTY_ID
from uap_analytics.regression.compare import ResultComparer
from uap_analytics.regression.fingerprint import InputFingerprint
from uap_analytics.regression.runner import RegressionRunner, summary_markdown


def test_comparer_tolerates_float_noise_and_ignores_manifest():
    a = {"manifest": {"run_id": "x"}, "tests": {"t": {"rate_ratio": 2.0, "p": 1e-30, "verdict": "confirmed", "n": float("nan")}}}
    b = {"manifest": {"run_id": "y"}, "tests": {"t": {"rate_ratio": 2.0 * (1 + 1e-9), "p": 1.1e-30, "verdict": "confirmed", "n": math.nan}}}
    assert ResultComparer().compare(a, b) == []


def test_comparer_reports_changed_values_keys_and_lengths():
    a = {"x": 1.0, "v": "refuted", "l": [1, 2], "gone": 1}
    b = {"x": 1.01, "v": "inconclusive", "l": [1], "new": 2}
    paths = {d.path for d in ResultComparer().compare(a, b)}
    assert paths == {"x", "v", "l[len]", "gone"}
    assert ResultComparer().added(a, b) == ["new"]      # a new output field is an addition, not a change


def test_comparer_does_not_treat_bools_as_numbers():
    assert ResultComparer().compare({"holds": True}, {"holds": 1}) != []


class _Table:
    def __init__(self, events):
        self.events = events


def test_fingerprint_is_order_independent_and_sensitive_to_changes():
    ev = pd.DataFrame({"event_id": [1, 2, 3], COUNTY_ID: ["01001", "01001", "06037"],
                       "night": pd.to_datetime(["2011-01-01", "2011-01-02", "2011-01-03"]),
                       "in_filtered": [True, False, True], "in_high_quality": [False, False, True]})
    a = InputFingerprint.of(_Table(ev))
    b = InputFingerprint.of(_Table(ev.iloc[::-1]))
    assert a == b and a["events"]["count"] == 3 and a["county_counts"]["counties"] == 2
    changed = ev.copy()
    changed.loc[0, COUNTY_ID] = "06037"
    assert InputFingerprint.of(_Table(changed))["events"]["sha256"] != a["events"]["sha256"]


def test_targets_find_committed_results(tmp_path):
    for hyp, split in (("H-a", "explore"), ("H-a", "confirm"), ("H-b", "explore"), ("H-x", "explore")):
        d = tmp_path / "results" / hyp / split
        d.mkdir(parents=True)
        (d / "results.json").write_text(json.dumps({}))
    runner = RegressionRunner(tmp_path, config=None, studies={"H-a": "m:A", "H-b": "m:B"})
    assert runner.targets() == [("H-a", "confirm"), ("H-a", "explore"), ("H-b", "explore")]
    assert runner.targets(only="H-a", split="confirm") == [("H-a", "confirm")]


def test_summary_marks_changes():
    checks = [{"hypothesis": "H-a", "split": "confirm", "ok": False, "error": None, "seconds": 60, "fingerprint": "match",
               "differences": ["x: committed 1, now 2"], "n_differences": 1, "fingerprint_differences": [], "inputs_changed": ["data/raw/airports/airports.csv"]}]
    text = summary_markdown(checks)
    assert "CHANGED" in text and "x: committed 1, now 2" in text and "raw input changed: data/raw/airports" in text




def test_changed_raw_file_alone_is_a_warning():
    from uap_analytics.regression.runner import RunCheck, summary_markdown
    check = RunCheck("H-x", "confirm", fingerprint="match", inputs_changed=["data/raw/a.csv"])
    assert check.ok
    md = summary_markdown([check.as_dict()])
    assert "same, raw differs" in md and "raw input changed: data/raw/a.csv" in md


def test_tolerance_absorbs_refit_noise():
    from uap_analytics.regression.compare import ResultComparer
    assert ResultComparer().compare({"p": 4.878239931526553e-07}, {"p": 4.878253435809939e-07}) == []
    assert ResultComparer().compare({"p": 1.0}, {"p": 1.0001})


