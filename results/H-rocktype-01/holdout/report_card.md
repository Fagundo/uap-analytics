# H-rocktype-01 report card: Rock type at the surface (screen of seven classes)

**Split:** holdout (2021–latest)  
**Run:** H-rocktype-01-holdout-20261119T233037Z  
**Code:** `2b85eae2e8f9`  
**Spec / impl / filters SHA-256:** `dcf76d6c1e07` / `33f303d84e39` / `8b2d4002b6f7`

## Question

At least one rock type at a county's surface goes with how many UAP events the county reports, beyond the observer controls, in either direction, and for that type the real geologic map lines up with reporting better than rigidly shifted copies of it.

## Verdicts

| Test | Verdict | Primary rate ratio (95% CI) | BH-adjusted p | Power for RR 1.10 |
| --- | --- | --- | --- | --- |
| Unconsolidated sediment (sand, gravel, clay, silt, glacial and alluvial deposits) (share, per SD) | **inconclusive** | 0.951 (0.889–1.017) | 0.607 | 77% |
| Clastic and other sedimentary rock (sandstone, shale, mudstone, conglomerate, chert, coal, evaporite) (share, per SD) | **refuted** | 1.009 (0.946–1.076) | 0.893 | 97% |
| Carbonate rock (limestone, dolostone, marlstone) (share, per SD) | **inconclusive** | 1.058 (0.976–1.147) | 0.607 | 100% |
| Volcanic and shallow intrusive rock (basalt, andesite, rhyolite, tuff, dikes) (share, per SD) | **inconclusive** | 1.038 (0.939–1.146) | 0.817 | 62% |
| Plutonic rock (granite, diorite, gabbro, syenite) (share, per SD) | **refuted** | 0.990 (0.944–1.038) | 0.893 | 100% |
| Metasedimentary rock (quartzite, slate, metasandstone, marble, paragneiss) (share, per SD) | **refuted** | 0.996 (0.939–1.056) | 0.893 | 95% |
| Schist, gneiss and other crystalline metamorphic rock (incl. tectonite) (share, per SD) | **refuted** | 0.978 (0.923–1.037) | 0.817 | 99% |

## Unconsolidated sediment (sand, gravel, clay, silt, glacial and alluvial deposits) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.949 | 0.887–1.016 | 0.130 | 3,100 | 3,957 |
| Filtered (explainable removed) | 0.951 | 0.889–1.017 | 0.139 | 3,100 | 3,909 |
| High quality | 0.891 | 0.804–0.989 | 0.030 | 3,100 | 1,633 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.951, p 0.423)

## Clastic and other sedimentary rock (sandstone, shale, mudstone, conglomerate, chert, coal, evaporite) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 1.015 | 0.952–1.083 | 0.642 | 3,100 | 3,957 |
| Filtered (explainable removed) | 1.009 | 0.946–1.076 | 0.790 | 3,100 | 3,909 |
| High quality | 1.045 | 0.951–1.149 | 0.357 | 3,100 | 1,633 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 1.009, p 0.836)

## Carbonate rock (limestone, dolostone, marlstone) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 1.058 | 0.975–1.148 | 0.175 | 3,100 | 3,957 |
| Filtered (explainable removed) | 1.058 | 0.976–1.147 | 0.173 | 3,100 | 3,909 |
| High quality | 1.039 | 0.943–1.145 | 0.439 | 3,100 | 1,633 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 1.058, p 0.114)

## Volcanic and shallow intrusive rock (basalt, andesite, rhyolite, tuff, dikes) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 1.040 | 0.941–1.151 | 0.442 | 3,100 | 3,957 |
| Filtered (explainable removed) | 1.038 | 0.939–1.146 | 0.467 | 3,100 | 3,909 |
| High quality | 1.043 | 0.948–1.148 | 0.385 | 3,100 | 1,633 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 1.038, p 0.393)

## Plutonic rock (granite, diorite, gabbro, syenite) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.989 | 0.943–1.037 | 0.648 | 3,100 | 3,957 |
| Filtered (explainable removed) | 0.990 | 0.944–1.038 | 0.671 | 3,100 | 3,909 |
| High quality | 1.013 | 0.947–1.082 | 0.711 | 3,100 | 1,633 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.990, p 0.731)

## Metasedimentary rock (quartzite, slate, metasandstone, marble, paragneiss) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.994 | 0.940–1.052 | 0.842 | 3,100 | 3,957 |
| Filtered (explainable removed) | 0.996 | 0.939–1.056 | 0.893 | 3,100 | 3,909 |
| High quality | 0.978 | 0.886–1.079 | 0.655 | 3,100 | 1,633 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.996, p 0.900)

## Schist, gneiss and other crystalline metamorphic rock (incl. tectonite) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.972 | 0.918–1.029 | 0.326 | 3,100 | 3,957 |
| Filtered (explainable removed) | 0.978 | 0.923–1.037 | 0.458 | 3,100 | 3,909 |
| High quality | 1.022 | 0.945–1.105 | 0.584 | 3,100 | 1,633 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.978, p 0.627)

## Rock-type classes

Classes come from each map unit's major lithologies (SGMC Lithology table, LITH1 and LITH2); a unit with several is split evenly.

| Class | Mean county share |
| --- | --- |
| Unconsolidated sediment (sand, gravel, clay, silt, glacial and alluvial deposits) | 26.6% |
| Clastic and other sedimentary rock (sandstone, shale, mudstone, conglomerate, chert, coal, evaporite) | 40.7% |
| Carbonate rock (limestone, dolostone, marlstone) | 17.0% |
| Volcanic and shallow intrusive rock (basalt, andesite, rhyolite, tuff, dikes) | 3.2% |
| Plutonic rock (granite, diorite, gabbro, syenite) | 2.9% |
| Metasedimentary rock (quartzite, slate, metasandstone, marble, paragneiss) | 2.5% |
| Schist, gneiss and other crystalline metamorphic rock (incl. tectonite) | 7.0% |

## Observed and expected events by dominant rock type (primary tier)

Expected counts come from the controls-only model; descriptive.

| Dominant type | Counties | Observed | Expected | Ratio |
| --- | --- | --- | --- | --- |
| unconsolidated | 818 | 1,359 | 1,608 | 0.85 |
| clastic | 1,365 | 1,160 | 1,153 | 1.01 |
| carbonate | 458 | 525 | 500 | 1.05 |
| volcanic | 100 | 197 | 210 | 0.94 |
| plutonic | 78 | 217 | 233 | 0.93 |
| metasedimentary | 55 | 64 | 66 | 0.97 |
| crystalline_metamorphic | 226 | 310 | 322 | 0.96 |

## Shift-test copies (primary tier)

| Class | Copies fitted | 2.5% | Median | 97.5% |
| --- | --- | --- | --- | --- |
| unconsolidated | 200 | 0.899 | 0.990 | 1.106 |
| clastic | 200 | 0.934 | 0.994 | 1.065 |
| carbonate | 200 | 0.915 | 1.005 | 1.062 |
| volcanic | 200 | 0.935 | 1.012 | 1.077 |
| plutonic | 200 | 0.939 | 1.001 | 1.067 |
| metasedimentary | 200 | 0.938 | 1.003 | 1.059 |
| crystalline_metamorphic | 200 | 0.932 | 1.009 | 1.083 |

Power: two-sided for rate ratio 1.10 or 1/1.10 at alpha 0.05/7, from the explore-period standard error of each share, not scaled down for more events.

map units with a rock type: 6,619; share of county cells on a classified unit: 0.991; counties with a rock type: 3,108.

## Data

- Reports 2001–latest after cleaning: 74,795; merged into 69,348 events (69,333 located in a county).
- Events explained at high confidence, by rule: meteor_fireball 1,461, nuforc_note 2,288, sky_lantern 56. Reports with only medium-confidence matches (kept): 4,980.

## Caveats

- Reports are self-selected and unverified; results describe reporting, not phenomena.
- Filter precision was checked against labels written by Claude (an AI), not by a human.
- Planet and ISS rules are not yet implemented; launch-matched rules run on text only (medium confidence).
- A rate ratio describes reporting on exposed nights versus the same places on matched nights; it does not identify a mechanism.
