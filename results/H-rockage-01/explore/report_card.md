# H-rockage-01 report card: Geologic age of surface rock

**Split:** explore (2001–2010)  
**Run:** H-rockage-01-explore-20261119T185646Z  
**Code:** `6d92ab408f0f`  
**Spec / impl / filters SHA-256:** `f7ed198eda88` / `1fa094b953dc` / `8b2d4002b6f7`

## Question

The geologic age of the rocks at a county's surface goes with how many UAP events the county reports, beyond the observer controls, in either direction, and the real geologic map lines up with reporting better than rigidly shifted copies of it.

This is an **exploration** run: it checks the pipeline and estimates power. Its estimates are shown for completeness and change nothing in the registered tests.

## Verdicts

| Test | Verdict | Primary rate ratio (95% CI) | BH-adjusted p | Power for RR 1.10 |
| --- | --- | --- | --- | --- |
| Mean geologic age of surface rock, log10 Ma (per SD; two-sided) | **exploration (no verdict)** | 1.041 (0.976–1.111) | 0.218 | 82% |

## Mean geologic age of surface rock, log10 Ma (per SD; two-sided)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 1.046 | 0.977–1.120 | 0.199 | 3,100 | 23,077 |
| Filtered (explainable removed) | 1.041 | 0.976–1.111 | 0.218 | 3,100 | 21,798 |
| High quality | 1.039 | 0.969–1.114 | 0.279 | 3,100 | 9,770 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 1.041, p 0.313)

## Secondary estimates: era shares (primary tier)

One model with the Mesozoic, Paleozoic and Precambrian shares of each county's dated cells (Cenozoic is the reference). Descriptive; no verdict.

| Term | Rate ratio | 95% CI | p |
| --- | --- | --- | --- |
| Mesozoic share (vs Cenozoic), per SD | 1.005 | 0.929–1.087 | 0.895 |
| Paleozoic share (vs Cenozoic), per SD | 1.097 | 1.007–1.195 | 0.0346 |
| Precambrian share (vs Cenozoic), per SD | 0.989 | 0.944–1.035 | 0.62 |

## Observed and expected events by dominant era (primary tier)

Expected counts come from the controls-only model; descriptive.

| Dominant era | Counties | Observed | Expected | Ratio |
| --- | --- | --- | --- | --- |
| Cenozoic | 1,101 | 10,021 | 11,745 | 0.85 |
| Mesozoic | 395 | 2,524 | 2,796 | 0.90 |
| Paleozoic | 1,285 | 7,096 | 6,967 | 1.02 |
| Precambrian | 319 | 1,938 | 2,011 | 0.96 |

Shift test: 200 of 200 copies fitted; their rate ratios run 0.930 (2.5%), 1.003 (median), 1.074 (97.5%).

Power inputs: explore SE 0.0330 on 21,798 events; this split 21,798 events, SE 0.0330.

counties: 3,108; counties with a dated surface unit: 3,108; counties from the centroid cell (smaller than a cell): 0.

## Data

- Reports 2001–latest after cleaning: 74,795; merged into 69,348 events (69,333 located in a county).
- Events explained at high confidence, by rule: meteor_fireball 1,461, nuforc_note 2,288, sky_lantern 56. Reports with only medium-confidence matches (kept): 4,980.

## Caveats

- Reports are self-selected and unverified; results describe reporting, not phenomena.
- Filter precision was checked against labels written by Claude (an AI), not by a human.
- Planet and ISS rules are not yet implemented; launch-matched rules run on text only (medium confidence).
- A rate ratio describes reporting on exposed nights versus the same places on matched nights; it does not identify a mechanism.
