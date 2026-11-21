# Regression baseline for the data refactor

The refactor (PURSUE builds the data, uap-geo reads its exports) must not move any committed result. Its
gate compares every rerun with a **baseline**: the result of rerunning each committed hypothesis split on
2026-11-20, before any refactor code changed. The registered `results.json` files stay as the historical
record; `regression_baseline.json` beside each one is what later reruns are compared with.

The first rerun (run 44831244921) compared the current code and data with the registered results. Every
difference had one of three causes, none of which changes a verdict:

| Cause | Where | Size | Why |
| --- | --- | --- | --- |
| New output field | All event studies (H-geo-01, H-launch-01, H-celebrate-01) | `dispersion` added per tier | The 2026-11-11 audit added the overdispersion estimate after these results were committed. Additions are now reported, not counted as changes. |
| Power formula fixed | H-install-01 and H-volcano-01, explore split | explore power 1.00 → 0.9995 and 1.00 → 0.31 | The audit replaced the negative-binomial power formula (it overstated power) with the explore-SE rule; the confirm results were rerun then, the explore results were not. |
| Live inputs re-downloaded | H-persist-01, H-install-01, H-volcano-01 (county studies) | Rate ratios moved by at most 4e-5 relative (H-volcano-01 confirm 1.07211 → 1.07215); p-values by ≤ 2e-4; no verdict changed | `data/raw/airports/airports.csv` (OurAirports, updated daily) and the GCAT launch lists differ from the files those runs used. Results computed since 2026-11-19 (H-rockage-01, H-rocktype-01, H-rockera-01) matched exactly. |

From the baseline on, each rerun also checks the SHA-256 of every raw input file the baseline used, so a
re-downloaded file is reported as such instead of as an unexplained change. Pinning raw inputs (a lock file
like PURSUE's `sources/lock.json`) is part of moving the data to PURSUE.

## Pinned raw inputs (2026-11-21)

The first comparison with the baselines (run 44841524097) reported re-downloaded files: the Smithsonian
volcano list (H-volcano-01; results identical) and the 2024 and 2026 earthquake files (H-geo-01; one p-value
moved by 3e-6 relative). Each hypothesis now restores its own pinned raw-data cache
(`regression-raw-<hypothesis>-v1`), saved by the rebaseline run, so later reruns use exactly the baseline's
files. The baselines were rewritten once more on that run; results were unchanged apart from those two items.
