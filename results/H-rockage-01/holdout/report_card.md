# H-rockage-01 report card: Geologic age of surface rock

**Split:** holdout (2021–latest)  
**Run:** H-rockage-01-holdout-20261119T194747Z  
**Code:** `d82e3614713e`  
**Spec / impl / filters SHA-256:** `2e9a834e98d4` / `1fa094b953dc` / `8b2d4002b6f7`

## Question

The geologic age of the rocks at a county's surface goes with how many UAP events the county reports, beyond the observer controls, in either direction, and the real geologic map lines up with reporting better than rigidly shifted copies of it.

## Verdicts

| Test | Verdict | Primary rate ratio (95% CI) | BH-adjusted p | Power for RR 1.10 |
| --- | --- | --- | --- | --- |
| Mean geologic age of surface rock, log10 Ma (per SD; two-sided) | **underpowered** | 1.057 (0.958–1.166) | 0.270 | 23% |

## Mean geologic age of surface rock, log10 Ma (per SD; two-sided)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 1.053 | 0.952–1.165 | 0.314 | 3,100 | 3,957 |
| Filtered (explainable removed) | 1.057 | 0.958–1.166 | 0.270 | 3,100 | 3,909 |
| High quality | 1.171 | 1.015–1.351 | 0.031 | 3,100 | 1,633 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 1.057, p 0.358)

## Secondary estimates: era shares (primary tier)

One model with the Mesozoic, Paleozoic and Precambrian shares of each county's dated cells (Cenozoic is the reference). Descriptive; no verdict.

| Term | Rate ratio | 95% CI | p |
| --- | --- | --- | --- |
| Mesozoic share (vs Cenozoic), per SD | 1.036 | 0.941–1.140 | 0.47 |
| Paleozoic share (vs Cenozoic), per SD | 1.061 | 0.942–1.195 | 0.333 |
| Precambrian share (vs Cenozoic), per SD | 1.000 | 0.931–1.075 | 0.994 |

## Observed and expected events by dominant era (primary tier)

Expected counts come from the controls-only model; descriptive.

| Dominant era | Counties | Observed | Expected | Ratio |
| --- | --- | --- | --- | --- |
| Cenozoic | 1,101 | 1,728 | 1,992 | 0.87 |
| Mesozoic | 395 | 444 | 453 | 0.98 |
| Paleozoic | 1,285 | 1,260 | 1,222 | 1.03 |
| Precambrian | 319 | 400 | 424 | 0.94 |

Shift test: 200 of 200 copies fitted; their rate ratios run 0.891 (2.5%), 1.011 (median), 1.121 (97.5%).

Power inputs: explore SE 0.0330 on 21,798 events; this split 3,909 events, SE 0.0780.

counties: 3,108; counties with a dated surface unit: 3,108; counties from the centroid cell (smaller than a cell): 0.

## Data

- Reports 2001–latest after cleaning: 74,795; merged into 69,348 events (69,333 located in a county).
- Events explained at high confidence, by rule: meteor_fireball 1,461, nuforc_note 2,288, sky_lantern 56. Reports with only medium-confidence matches (kept): 4,980.

## Caveats

- Reports are self-selected and unverified; results describe reporting, not phenomena.
- Filter precision was checked against labels written by Claude (an AI), not by a human.
- Planet and ISS rules are not yet implemented; launch-matched rules run on text only (medium confidence).
- A rate ratio describes reporting on exposed nights versus the same places on matched nights; it does not identify a mechanism.
