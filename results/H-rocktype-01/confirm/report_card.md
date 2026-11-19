# H-rocktype-01 report card: Rock type at the surface (screen of seven classes)

**Split:** confirm (2011–2020)  
**Run:** H-rocktype-01-confirm-20261119T223941Z  
**Code:** `4bbbeeb952ff`  
**Spec / impl / filters SHA-256:** `dcf76d6c1e07` / `33f303d84e39` / `8b2d4002b6f7`

## Question

At least one rock type at a county's surface goes with how many UAP events the county reports, beyond the observer controls, in either direction, and for that type the real geologic map lines up with reporting better than rigidly shifted copies of it.

## Verdicts

| Test | Verdict | Primary rate ratio (95% CI) | BH-adjusted p | Power for RR 1.10 |
| --- | --- | --- | --- | --- |
| Unconsolidated sediment (sand, gravel, clay, silt, glacial and alluvial deposits) (share, per SD) | **inconclusive** | 0.972 (0.917–1.031) | 0.598 | 77% |
| Clastic and other sedimentary rock (sandstone, shale, mudstone, conglomerate, chert, coal, evaporite) (share, per SD) | **refuted** | 0.995 (0.955–1.037) | 0.818 | 97% |
| Carbonate rock (limestone, dolostone, marlstone) (share, per SD) | **confirmed (more reports)** | 1.062 (1.034–1.090) | < 0.001 | 100% |
| Volcanic and shallow intrusive rock (basalt, andesite, rhyolite, tuff, dikes) (share, per SD) | **inconclusive** | 1.016 (0.964–1.071) | 0.767 | 62% |
| Plutonic rock (granite, diorite, gabbro, syenite) (share, per SD) | **refuted** | 0.964 (0.932–0.998) | 0.133 | 100% |
| Metasedimentary rock (quartzite, slate, metasandstone, marble, paragneiss) (share, per SD) | **refuted** | 1.005 (0.973–1.038) | 0.818 | 95% |
| Schist, gneiss and other crystalline metamorphic rock (incl. tectonite) (share, per SD) | **refuted** | 0.969 (0.925–1.015) | 0.436 | 99% |

## Unconsolidated sediment (sand, gravel, clay, silt, glacial and alluvial deposits) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.968 | 0.913–1.027 | 0.286 | 3,100 | 38,555 |
| Filtered (explainable removed) | 0.972 | 0.917–1.031 | 0.342 | 3,100 | 36,684 |
| High quality | 0.964 | 0.907–1.024 | 0.232 | 3,100 | 17,541 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.972, p 0.507)

## Clastic and other sedimentary rock (sandstone, shale, mudstone, conglomerate, chert, coal, evaporite) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.999 | 0.960–1.040 | 0.963 | 3,100 | 38,555 |
| Filtered (explainable removed) | 0.995 | 0.955–1.037 | 0.818 | 3,100 | 36,684 |
| High quality | 0.968 | 0.927–1.011 | 0.147 | 3,100 | 17,541 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.995, p 0.836)

## Carbonate rock (limestone, dolostone, marlstone) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 1.058 | 1.031–1.085 | < 0.001 | 3,100 | 38,555 |
| Filtered (explainable removed) | 1.062 | 1.034–1.090 | < 0.001 | 3,100 | 36,684 |
| High quality | 1.074 | 1.037–1.113 | < 0.001 | 3,100 | 17,541 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **holds** (rate ratio 1.062, p 0.020)

## Volcanic and shallow intrusive rock (basalt, andesite, rhyolite, tuff, dikes) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 1.019 | 0.969–1.072 | 0.464 | 3,100 | 38,555 |
| Filtered (explainable removed) | 1.016 | 0.964–1.071 | 0.548 | 3,100 | 36,684 |
| High quality | 1.037 | 0.981–1.097 | 0.202 | 3,100 | 17,541 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 1.016, p 0.627)

## Plutonic rock (granite, diorite, gabbro, syenite) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.966 | 0.934–1.000 | 0.050 | 3,100 | 38,555 |
| Filtered (explainable removed) | 0.964 | 0.932–0.998 | 0.038 | 3,100 | 36,684 |
| High quality | 0.961 | 0.930–0.993 | 0.018 | 3,100 | 17,541 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **holds** (rate ratio 0.964, p 0.050)

## Metasedimentary rock (quartzite, slate, metasandstone, marble, paragneiss) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 1.007 | 0.974–1.041 | 0.679 | 3,100 | 38,555 |
| Filtered (explainable removed) | 1.005 | 0.973–1.038 | 0.759 | 3,100 | 36,684 |
| High quality | 1.024 | 0.984–1.065 | 0.244 | 3,100 | 17,541 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 1.005, p 0.796)

## Schist, gneiss and other crystalline metamorphic rock (incl. tectonite) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.969 | 0.927–1.014 | 0.173 | 3,100 | 38,555 |
| Filtered (explainable removed) | 0.969 | 0.925–1.015 | 0.187 | 3,100 | 36,684 |
| High quality | 0.987 | 0.942–1.033 | 0.566 | 3,100 | 17,541 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.969, p 0.289)

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
| unconsolidated | 818 | 12,522 | 15,247 | 0.82 |
| clastic | 1,365 | 10,717 | 10,848 | 0.99 |
| carbonate | 458 | 5,337 | 5,027 | 1.06 |
| volcanic | 100 | 1,923 | 1,937 | 0.99 |
| plutonic | 78 | 1,836 | 2,189 | 0.84 |
| metasedimentary | 55 | 716 | 747 | 0.96 |
| crystalline_metamorphic | 226 | 3,069 | 3,272 | 0.94 |

## Shift-test copies (primary tier)

| Class | Copies fitted | 2.5% | Median | 97.5% |
| --- | --- | --- | --- | --- |
| unconsolidated | 200 | 0.940 | 0.996 | 1.093 |
| clastic | 200 | 0.938 | 0.999 | 1.043 |
| carbonate | 200 | 0.956 | 1.005 | 1.052 |
| volcanic | 200 | 0.964 | 1.016 | 1.066 |
| plutonic | 200 | 0.964 | 0.996 | 1.028 |
| metasedimentary | 200 | 0.964 | 0.994 | 1.038 |
| crystalline_metamorphic | 200 | 0.949 | 1.000 | 1.053 |

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
