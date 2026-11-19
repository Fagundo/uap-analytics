# H-rocktype-01 report card: Rock type at the surface (screen of seven classes)

**Split:** explore (2001–2010)  
**Run:** H-rocktype-01-explore-20261119T214727Z  
**Code:** `57d9e083128c`  
**Spec / impl / filters SHA-256:** `a3299e28663d` / `33f303d84e39` / `8b2d4002b6f7`

## Question

At least one rock type at a county's surface goes with how many UAP events the county reports, beyond the observer controls, in either direction, and for that type the real geologic map lines up with reporting better than rigidly shifted copies of it.

This is an **exploration** run: it checks the pipeline and estimates power. Its estimates are shown for completeness and change nothing in the registered tests.

## Verdicts

| Test | Verdict | Primary rate ratio (95% CI) | BH-adjusted p | Power for RR 1.10 |
| --- | --- | --- | --- | --- |
| Unconsolidated sediment (sand, gravel, clay, silt, glacial and alluvial deposits) (share, per SD) | **exploration (no verdict)** | 0.946 (0.896–0.998) | 0.151 | 77% |
| Clastic and other sedimentary rock (sandstone, shale, mudstone, conglomerate, chert, coal, evaporite) (share, per SD) | **exploration (no verdict)** | 1.044 (1.003–1.087) | 0.151 | 97% |
| Carbonate rock (limestone, dolostone, marlstone) (share, per SD) | **exploration (no verdict)** | 1.020 (0.988–1.053) | 0.395 | 100% |
| Volcanic and shallow intrusive rock (basalt, andesite, rhyolite, tuff, dikes) (share, per SD) | **exploration (no verdict)** | 0.987 (0.927–1.050) | 0.673 | 62% |
| Plutonic rock (granite, diorite, gabbro, syenite) (share, per SD) | **exploration (no verdict)** | 0.986 (0.963–1.009) | 0.395 | 100% |
| Metasedimentary rock (quartzite, slate, metasandstone, marble, paragneiss) (share, per SD) | **exploration (no verdict)** | 1.014 (0.972–1.059) | 0.593 | 95% |
| Schist, gneiss and other crystalline metamorphic rock (incl. tectonite) (share, per SD) | **exploration (no verdict)** | 0.986 (0.950–1.024) | 0.593 | 99% |

## Unconsolidated sediment (sand, gravel, clay, silt, glacial and alluvial deposits) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.939 | 0.888–0.994 | 0.029 | 3,100 | 23,077 |
| Filtered (explainable removed) | 0.946 | 0.896–0.998 | 0.043 | 3,100 | 21,798 |
| High quality | 0.934 | 0.880–0.992 | 0.026 | 3,100 | 9,770 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.946, p 0.164)

## Clastic and other sedimentary rock (sandstone, shale, mudstone, conglomerate, chert, coal, evaporite) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 1.043 | 0.999–1.088 | 0.056 | 3,100 | 23,077 |
| Filtered (explainable removed) | 1.044 | 1.003–1.087 | 0.037 | 3,100 | 21,798 |
| High quality | 1.072 | 1.020–1.126 | 0.006 | 3,100 | 9,770 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 1.044, p 0.109)

## Carbonate rock (limestone, dolostone, marlstone) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 1.023 | 0.988–1.060 | 0.204 | 3,100 | 23,077 |
| Filtered (explainable removed) | 1.020 | 0.988–1.053 | 0.226 | 3,100 | 21,798 |
| High quality | 1.015 | 0.973–1.060 | 0.481 | 3,100 | 9,770 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 1.020, p 0.468)

## Volcanic and shallow intrusive rock (basalt, andesite, rhyolite, tuff, dikes) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.989 | 0.929–1.053 | 0.733 | 3,100 | 23,077 |
| Filtered (explainable removed) | 0.987 | 0.927–1.050 | 0.673 | 3,100 | 21,798 |
| High quality | 0.981 | 0.922–1.044 | 0.544 | 3,100 | 9,770 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.987, p 0.662)

## Plutonic rock (granite, diorite, gabbro, syenite) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.986 | 0.963–1.009 | 0.223 | 3,100 | 23,077 |
| Filtered (explainable removed) | 0.986 | 0.963–1.009 | 0.220 | 3,100 | 21,798 |
| High quality | 0.976 | 0.944–1.008 | 0.140 | 3,100 | 9,770 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.986, p 0.438)

## Metasedimentary rock (quartzite, slate, metasandstone, marble, paragneiss) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 1.016 | 0.973–1.061 | 0.474 | 3,100 | 23,077 |
| Filtered (explainable removed) | 1.014 | 0.972–1.059 | 0.509 | 3,100 | 21,798 |
| High quality | 1.014 | 0.974–1.055 | 0.499 | 3,100 | 9,770 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 1.014, p 0.493)

## Schist, gneiss and other crystalline metamorphic rock (incl. tectonite) (share, per SD)

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.989 | 0.952–1.026 | 0.553 | 3,100 | 23,077 |
| Filtered (explainable removed) | 0.986 | 0.950–1.024 | 0.470 | 3,100 | 21,798 |
| High quality | 0.980 | 0.937–1.025 | 0.388 | 3,100 | 9,770 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.986, p 0.617)

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
| unconsolidated | 818 | 7,745 | 9,558 | 0.81 |
| clastic | 1,365 | 6,591 | 6,529 | 1.01 |
| carbonate | 458 | 3,229 | 3,254 | 0.99 |
| volcanic | 100 | 1,018 | 1,085 | 0.94 |
| plutonic | 78 | 1,062 | 1,191 | 0.89 |
| metasedimentary | 55 | 319 | 306 | 1.04 |
| crystalline_metamorphic | 226 | 1,615 | 1,599 | 1.01 |

## Shift-test copies (primary tier)

| Class | Copies fitted | 2.5% | Median | 97.5% |
| --- | --- | --- | --- | --- |
| unconsolidated | 200 | 0.930 | 0.990 | 1.095 |
| clastic | 200 | 0.950 | 1.004 | 1.055 |
| carbonate | 200 | 0.949 | 1.000 | 1.052 |
| volcanic | 200 | 0.970 | 1.014 | 1.064 |
| plutonic | 200 | 0.968 | 0.998 | 1.041 |
| metasedimentary | 200 | 0.964 | 1.000 | 1.036 |
| crystalline_metamorphic | 200 | 0.949 | 1.003 | 1.049 |

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
