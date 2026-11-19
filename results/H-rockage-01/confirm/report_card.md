# H-rockage-01 report card: Geologic age of surface rock

**Split:** confirm (2011–2020)  
**Run:** H-rockage-01-confirm-20261119T193946Z  
**Code:** `2aa9ae617af9`  
**Spec / impl / filters SHA-256:** `2e9a834e98d4` / `1fa094b953dc` / `8b2d4002b6f7`

## Question

The geologic age of the rocks at a county's surface goes with how many UAP events the county reports, beyond the observer controls, in either direction, and the real geologic map lines up with reporting better than rigidly shifted copies of it.

## Verdicts

| Test | Verdict | Primary rate ratio (95% CI) | BH-adjusted p | Power for RR 1.10 |
| --- | --- | --- | --- | --- |
| Mean geologic age of surface rock, log10 Ma (per SD; two-sided) | **refuted** | 0.993 (0.920–1.073) | 0.868 | 96% |

## Mean geologic age of surface rock, log10 Ma (per SD; two-sided)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.999 | 0.926–1.078 | 0.981 | 3,100 | 38,555 |
| Filtered (explainable removed) | 0.993 | 0.920–1.073 | 0.868 | 3,100 | 36,684 |
| High quality | 0.995 | 0.917–1.081 | 0.911 | 3,100 | 17,541 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.993, p 0.811)

## Secondary estimates: era shares (primary tier)

One model with the Mesozoic, Paleozoic and Precambrian shares of each county's dated cells (Cenozoic is the reference). Descriptive; no verdict.

| Term | Rate ratio | 95% CI | p |
| --- | --- | --- | --- |
| Mesozoic share (vs Cenozoic), per SD | 0.959 | 0.888–1.035 | 0.28 |
| Paleozoic share (vs Cenozoic), per SD | 1.088 | 1.006–1.177 | 0.0358 |
| Precambrian share (vs Cenozoic), per SD | 0.966 | 0.910–1.026 | 0.266 |

## Observed and expected events by dominant era (primary tier)

Expected counts come from the controls-only model; descriptive.

| Dominant era | Counties | Observed | Expected | Ratio |
| --- | --- | --- | --- | --- |
| Cenozoic | 1,101 | 16,167 | 18,584 | 0.87 |
| Mesozoic | 395 | 3,531 | 4,362 | 0.81 |
| Paleozoic | 1,285 | 12,610 | 12,123 | 1.04 |
| Precambrian | 319 | 3,812 | 4,198 | 0.91 |

Shift test: 200 of 200 copies fitted; their rate ratios run 0.926 (2.5%), 0.998 (median), 1.052 (97.5%).

Power inputs: explore SE 0.0330 on 21,798 events; this split 36,684 events, SE 0.0255.

counties: 3,108; counties with a dated surface unit: 3,108; counties from the centroid cell (smaller than a cell): 0.

## Data

- Reports 2001–latest after cleaning: 74,795; merged into 69,348 events (69,333 located in a county).
- Events explained at high confidence, by rule: meteor_fireball 1,461, nuforc_note 2,288, sky_lantern 56. Reports with only medium-confidence matches (kept): 4,980.

## Caveats

- Reports are self-selected and unverified; results describe reporting, not phenomena.
- Filter precision was checked against labels written by Claude (an AI), not by a human.
- Planet and ISS rules are not yet implemented; launch-matched rules run on text only (medium confidence).
- A rate ratio describes reporting on exposed nights versus the same places on matched nights; it does not identify a mechanism.
