# H-hatchpal-01 report card: Paleozoic surface rock in an independent catalog (Hatch UFO database, 1950-1999)

**Split:** explore (1950–1959)  
**Run:** H-hatchpal-01-explore-20261122T025704Z  
**Code:** `995ade6abebc`  
**Spec / impl / filters SHA-256:** `f748449bc89c` / `5637d50857f0` / `8b2d4002b6f7`

## Question

Counties with more Paleozoic surface rock have more Hatch UFO records, per person, beyond the observer controls, as NUFORC reports showed for 2001-2023 (H-rockera-01, post hoc: 1.106 per SD, layer-shift p 0.005). Tested two-sided; a confirmed effect in the opposite direction counts against the NUFORC finding.

This is an **exploration** run: it checks the pipeline and estimates power. Its estimates are shown for completeness and change nothing in the registered tests.

## Verdicts

| Test | Verdict | Primary rate ratio (95% CI) | BH-adjusted p | Power for RR 1.10 |
| --- | --- | --- | --- | --- |
| Paleozoic share of surface rock (per SD) | **exploration (no verdict)** | 0.975 (0.840–1.131) | 0.737 | 24% |

## Paleozoic share of surface rock (per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.975 | 0.840–1.131 | 0.737 | 3,107 | 2,359 |
| Filtered (explainable removed) | 0.975 | 0.840–1.131 | 0.737 | 3,107 | 2,356 |
| high_strangeness | 0.940 | 0.651–1.358 | 0.741 | 3,107 | 226 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.975, p 0.821)

## Hatch records

| Step | Records |
| --- | --- |
| hatch rows | 17,926 |
| in the U.S. | 7,912 |
| in the contiguous states | 7,730 |
| dated 1950-1999 | 6,888 |
| with coordinates | 6,888 |
| not flagged as a hoax | 6,816 |
| one per duplicate group | 6,711 |
| in a county with a population history | 6,547 |

Mean county Paleozoic share: 41.0%. Offset: mean county population over the 1950, 1960, 1970, 1980, 1990 censuses; 1 of 3,108 counties have none and are left out.

## By decade (filtered tier, per SD; descriptive)

| Years | Records | Rate ratio (95% CI) |
| --- | --- | --- |
| 1950-1959 | 2,356 | 0.975 (0.840–1.131) |

## Paleozoic carbonate and other Paleozoic rock (joint model, filtered tier; descriptive)

| Model | Term | Rate ratio (95% CI) | p |
| --- | --- | --- | --- |
| Paleozoic split by carbonate | paleozoic_carbonate | 0.989 (0.894–1.094) | 0.828 |
| Paleozoic split by carbonate | paleozoic_noncarbonate | 0.978 (0.873–1.095) | 0.694 |

Shift-test copies fitted: 200; rate ratio 2.5% 0.836, median 0.937, 97.5% 1.069.

Power: two-sided for rate ratio 1.10 or 1/1.10 at alpha 0.05, from the explore-period standard error (0.076, 2,356 records).

Hatch caveats: the catalog was compiled by one person from press, NICAP, Blue Book and other files up to the early 2000s, so its coverage follows what was reported and collected, not what was seen. The observer controls are today's (light pollution, roads, airports, census shares), an approximation for 1950-1999; the offset is the period's population. Report-card notes about matched nights and NUFORC rules do not apply to this study.

## Data

- Reports 1950–latest after cleaning: 2,359; merged into 2,359 events (2,359 located in a county).
- Events explained at high confidence, by rule: explained by PURSUE's flags (left out of the filtered tier) 3. Reports with only medium-confidence matches (kept): 0.

## Caveats

- Reports are self-selected and unverified; results describe reporting, not phenomena.
- Filter precision was checked against labels written by Claude (an AI), not by a human.
- Planet and ISS rules are not yet implemented; launch-matched rules run on text only (medium confidence).
- A rate ratio describes reporting on exposed nights versus the same places on matched nights; it does not identify a mechanism.
