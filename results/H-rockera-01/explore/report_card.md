# H-rockera-01 report card: Geologic era as the class, and era crossed with rock type (post hoc)

**Split:** explore (2001–2023)  
**Run:** H-rockera-01-explore-20261120T155507Z  
**Code:** `23b9adbe3382`  
**Spec / impl / filters SHA-256:** `040f67e80971` / `fdb539705e19` / `8b2d4002b6f7`

## Question

Descriptive: which eras of surface rock, and which era x rock-type combinations, go with how many UAP events a county reports beyond the observer controls; and whether the Paleozoic association (H-rockage-01 secondary) is carried by carbonate rock (H-rocktype-01) or by age.

This is an **exploration** run: it checks the pipeline and estimates power. Its estimates are shown for completeness and change nothing in the registered tests.

## Verdicts

| Test | Verdict | Primary rate ratio (95% CI) | BH-adjusted p | Power for RR 1.10 |
| --- | --- | --- | --- | --- |
| cenozoic | **post hoc (no verdict)** | 0.994 (0.926–1.067) | 0.871 | nan% |
| mesozoic | **post hoc (no verdict)** | 0.967 (0.900–1.040) | 0.456 | nan% |
| paleozoic | **post hoc (no verdict)** | 1.106 (1.046–1.169) | 0.005 | nan% |
| precambrian | **post hoc (no verdict)** | 0.962 (0.921–1.004) | 0.232 | nan% |
| cenozoic_unconsolidated | **post hoc (no verdict)** | 0.975 (0.922–1.032) | 0.456 | nan% |
| cenozoic_clastic | **post hoc (no verdict)** | 1.006 (0.953–1.062) | 0.871 | nan% |
| cenozoic_volcanic | **post hoc (no verdict)** | 1.027 (0.974–1.083) | 0.456 | nan% |
| mesozoic_unconsolidated | **post hoc (no verdict)** | 0.969 (0.950–0.989) | 0.009 | nan% |
| mesozoic_clastic | **post hoc (no verdict)** | 0.961 (0.908–1.017) | 0.294 | nan% |
| paleozoic_clastic | **post hoc (no verdict)** | 1.033 (0.990–1.078) | 0.294 | nan% |
| paleozoic_carbonate | **post hoc (no verdict)** | 1.036 (1.015–1.058) | 0.005 | nan% |
| precambrian_crystalline_metamorphic | **post hoc (no verdict)** | 0.962 (0.913–1.014) | 0.294 | nan% |

## cenozoic

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.990 | 0.920–1.064 | 0.783 | 3,100 | 65,589 |
| Filtered (explainable removed) | 0.994 | 0.926–1.067 | 0.871 | 3,100 | 62,391 |
| High quality | 0.988 | 0.927–1.054 | 0.720 | 3,100 | 28,944 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.994, p 0.915)

## mesozoic

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.969 | 0.901–1.042 | 0.394 | 3,100 | 65,589 |
| Filtered (explainable removed) | 0.967 | 0.900–1.040 | 0.366 | 3,100 | 62,391 |
| High quality | 0.960 | 0.902–1.022 | 0.203 | 3,100 | 28,944 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.967, p 0.254)

## paleozoic

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 1.107 | 1.044–1.175 | < 0.001 | 3,100 | 65,589 |
| Filtered (explainable removed) | 1.106 | 1.046–1.169 | < 0.001 | 3,100 | 62,391 |
| High quality | 1.117 | 1.058–1.180 | < 0.001 | 3,100 | 28,944 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **holds** (rate ratio 1.106, p 0.005)

## precambrian

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.963 | 0.924–1.004 | 0.079 | 3,100 | 65,589 |
| Filtered (explainable removed) | 0.962 | 0.921–1.004 | 0.077 | 3,100 | 62,391 |
| High quality | 0.970 | 0.924–1.017 | 0.209 | 3,100 | 28,944 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.962, p 0.085)

## cenozoic_unconsolidated

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.971 | 0.916–1.029 | 0.314 | 3,100 | 65,589 |
| Filtered (explainable removed) | 0.975 | 0.922–1.032 | 0.380 | 3,100 | 62,391 |
| High quality | 0.967 | 0.912–1.025 | 0.260 | 3,100 | 28,944 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.975, p 0.547)

## cenozoic_clastic

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 1.005 | 0.954–1.059 | 0.841 | 3,100 | 65,589 |
| Filtered (explainable removed) | 1.006 | 0.953–1.062 | 0.828 | 3,100 | 62,391 |
| High quality | 1.011 | 0.969–1.054 | 0.622 | 3,100 | 28,944 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 1.006, p 0.846)

## cenozoic_volcanic

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 1.029 | 0.978–1.084 | 0.269 | 3,100 | 65,589 |
| Filtered (explainable removed) | 1.027 | 0.974–1.083 | 0.326 | 3,100 | 62,391 |
| High quality | 1.038 | 0.980–1.100 | 0.204 | 3,100 | 28,944 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 1.027, p 0.413)

## mesozoic_unconsolidated

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.968 | 0.950–0.987 | 0.001 | 3,100 | 65,589 |
| Filtered (explainable removed) | 0.969 | 0.950–0.989 | 0.002 | 3,100 | 62,391 |
| High quality | 0.969 | 0.950–0.989 | 0.002 | 3,100 | 28,944 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.969, p 0.060)

## mesozoic_clastic

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.963 | 0.911–1.018 | 0.184 | 3,100 | 65,589 |
| Filtered (explainable removed) | 0.961 | 0.908–1.017 | 0.171 | 3,100 | 62,391 |
| High quality | 0.970 | 0.911–1.034 | 0.350 | 3,100 | 28,944 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.961, p 0.259)

## paleozoic_clastic

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 1.036 | 0.991–1.083 | 0.116 | 3,100 | 65,589 |
| Filtered (explainable removed) | 1.033 | 0.990–1.078 | 0.129 | 3,100 | 62,391 |
| High quality | 1.019 | 0.979–1.062 | 0.357 | 3,100 | 28,944 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 1.033, p 0.219)

## paleozoic_carbonate

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 1.034 | 1.012–1.056 | 0.002 | 3,100 | 65,589 |
| Filtered (explainable removed) | 1.036 | 1.015–1.058 | < 0.001 | 3,100 | 62,391 |
| High quality | 1.050 | 1.014–1.087 | 0.006 | 3,100 | 28,944 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 1.036, p 0.124)

## precambrian_crystalline_metamorphic

| Tier | Rate ratio | 95% CI | p | Strata | Events |
| --- | --- | --- | --- | --- | --- |
| All events | 0.963 | 0.915–1.014 | 0.153 | 3,100 | 65,589 |
| Filtered (explainable removed) | 0.962 | 0.913–1.014 | 0.149 | 3,100 | 62,391 |
| High quality | 0.967 | 0.912–1.026 | 0.264 | 3,100 | 28,944 |

**Discriminating checks (primary tier)**

- Real map beats rigidly shifted copies in absolute effect (two-sided p < 0.05): **does not hold** (rate ratio 0.962, p 0.139)

## Post-hoc status

Every year of data was seen before this analysis (H-rockage-01 and H-rocktype-01). Estimates and shift tests here describe the data; they confirm nothing. Power is not computed.

## Classes and estimates by period (filtered tier, per SD)

| Class | Mean county share | Pooled 2001–2023 | 2001–2010 | 2011–2020 | 2021–2023 | Shift p (pooled) |
| --- | --- | --- | --- | --- | --- | --- |
| cenozoic | 35.4% | 0.994 (0.926–1.067) | 0.973 (0.897–1.056) | 1.010 (0.940–1.086) | 0.963 (0.860–1.078) | 0.915 |
| mesozoic | 13.4% | 0.967 (0.900–1.040) | 0.989 (0.922–1.061) | 0.948 (0.883–1.018) | 1.024 (0.940–1.116) | 0.254 |
| paleozoic | 41.0% | 1.106 (1.046–1.169) | 1.101 (1.038–1.168) | 1.128 (1.061–1.199) | 1.042 (0.957–1.134) | 0.005 |
| precambrian | 10.2% | 0.962 (0.921–1.004) | 0.967 (0.934–1.000) | 0.952 (0.906–1.002) | 0.982 (0.930–1.036) | 0.085 |
| cenozoic unconsolidated | 24.5% | 0.975 (0.922–1.032) | 0.961 (0.904–1.022) | 0.992 (0.931–1.056) | 0.947 (0.877–1.022) | 0.547 |
| cenozoic clastic | 7.0% | 1.006 (0.953–1.062) | 1.000 (0.946–1.056) | 1.002 (0.955–1.051) | 1.001 (0.911–1.101) | 0.846 |
| cenozoic volcanic | 2.6% | 1.027 (0.974–1.083) | 0.999 (0.936–1.066) | 1.040 (0.989–1.094) | 1.018 (0.916–1.131) | 0.413 |
| mesozoic unconsolidated | 2.0% | 0.969 (0.950–0.989) | 0.969 (0.944–0.993) | 0.965 (0.944–0.986) | 0.998 (0.950–1.047) | 0.060 |
| mesozoic clastic | 8.7% | 0.961 (0.908–1.017) | 1.001 (0.939–1.066) | 0.946 (0.887–1.009) | 0.977 (0.899–1.063) | 0.259 |
| paleozoic clastic | 24.5% | 1.033 (0.990–1.078) | 1.057 (1.011–1.104) | 1.025 (0.982–1.071) | 1.016 (0.938–1.101) | 0.219 |
| paleozoic carbonate | 14.0% | 1.036 (1.015–1.058) | 1.001 (0.978–1.025) | 1.059 (1.033–1.086) | 1.012 (0.943–1.087) | 0.124 |
| precambrian crystalline metamorphic | 5.9% | 0.962 (0.913–1.014) | 0.967 (0.928–1.007) | 0.956 (0.903–1.012) | 0.956 (0.911–1.004) | 0.139 |

## Era against rock type (joint models, pooled 2001–2023, filtered tier, per SD)

| Model | Term | Rate ratio (95% CI) | p |
| --- | --- | --- | --- |
| Paleozoic and carbonate | paleozoic | 1.088 (1.023–1.158) | 0.00758 |
| Paleozoic and carbonate | carbonate | 1.027 (0.993–1.063) | 0.123 |
| Paleozoic split by carbonate | paleozoic_carbonate | 1.066 (1.034–1.100) | 4.74e-05 |
| Paleozoic split by carbonate | paleozoic_noncarbonate | 1.077 (1.025–1.131) | 0.0032 |
| Carbonate split by era | paleozoic_carbonate | 1.036 (1.015–1.058) | 0.000748 |
| Carbonate split by era | carbonate_nonpaleozoic | 1.042 (0.999–1.086) | 0.0561 |

Crosses kept when their mean county share is at least 2% (decided from the map alone).

## Data

- Reports 2001–latest after cleaning: 74,795; merged into 69,348 events (69,333 located in a county).
- Events explained at high confidence, by rule: meteor_fireball 1,461, nuforc_note 2,288, sky_lantern 56. Reports with only medium-confidence matches (kept): 4,980.

## Caveats

- Reports are self-selected and unverified; results describe reporting, not phenomena.
- Filter precision was checked against labels written by Claude (an AI), not by a human.
- Planet and ISS rules are not yet implemented; launch-matched rules run on text only (medium confidence).
- A rate ratio describes reporting on exposed nights versus the same places on matched nights; it does not identify a mechanism.
