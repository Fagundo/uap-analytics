# Post hoc: one geology model over every catalog, each compared within itself

Question: is the Paleozoic (and carbonate) association one effect across catalogs and decades, or a feature of
the NUFORC era? Exploratory, descriptive, not registered.

Data: county x decade x catalog rows (NUFORC, Hatch, NICAP, Blue Book index and unknowns together), 1950-2023,
selected as in the combined run (contiguous U.S., site or town level, not a hoax, NUFORC repeat or explained).
A case found in several catalogs is counted once, under the source closest to the original report: PURSUE's
government documents, then Blue Book, then NUFORC (first-hand reports), then the compilations NICAP, Hatch,
Magonia. Catalog-decade strata with fewer than ``MIN_STRATUM`` records are left out (Magonia and PURSUE's
incidents have too few to form any).

Model: Poisson pseudo-maximum likelihood (ppmlhdfe, via pyfixest) with catalog x state x decade fixed effects,
so every comparison is between counties of one state, in one decade, as one catalog saw them. The exposure is
the county's population at the decade's census x years; it enters as Poisson weights on the rate (the same
estimating equations as a log-exposure offset). Controls: the H-persist-01 set (today's values). Standard
errors clustered by state. Shares and controls are standardized over counties (rate ratio per SD).

Two weightings:
  natural   every record counts once (NUFORC carries most of the weight)
  balanced  every catalog-decade stratum carries the same total weight, however many records it has
Plus: the slope before and from 1980 (interaction), NUFORC against Hatch where both cover the same decades,
and every stratum's own estimate with a random-effects meta-analysis across them (I^2: how much the strata
disagree beyond chance).

## Records

| Step | Records |
| --- | --- |
| rows in the export | 130,265 |
| contiguous states | 102,617 |
| placed at site or town level | 98,978 |
| dated 1950-2023 | 97,657 |
| not a hoax or NUFORC repeat | 97,555 |
| not explained (filtered) | 92,649 |
| in a county with populations for every decade | 90,783 |
| one per case (first-hand source kept) | 88,659 |
| in the stacked model (strata of 100+ records) | 88,450 |

Strata: Blue Book 1950s 659, Blue Book 1960s 335, Hatch 1950s 1,830, Hatch 1960s 875, Hatch 1970s 1,049, Hatch 1980s 572, Hatch 1990s 711, NICAP 1950s 505, NICAP 1960s 538, NICAP 1970s 335, NICAP 1980s 143, NUFORC 1950s 307, NUFORC 1960s 912, NUFORC 1970s 1,677, NUFORC 1980s 1,427, NUFORC 1990s 5,794, NUFORC 2000s 22,881, NUFORC 2010s 39,742, NUFORC 2020s 8,158.

Rate ratio per SD (95% CI); * p < 0.05, ** p < 0.01.

## Paleozoic share

| Model | Rate ratio per SD |
| --- | --- |
| All strata, natural weighting | 1.171 (1.068–1.284)** |
| All strata, balanced weighting | 1.096 (1.005–1.196)* |
| Before 1980 (all catalogs) | 1.078 (0.968–1.201) |
| From 1980 (all catalogs) | 1.184 (1.076–1.302)** |
| Difference, from 1980 vs before (ratio of ratios) | 1.098 (0.998–1.208) |
| Same decades (1950s, 1960s, 1970s, 1980s, 1990s): Hatch | 1.056 (0.941–1.185) |
| Same decades: NUFORC | 1.199 (1.070–1.343)** |
| Same decades: NUFORC vs Hatch (ratio of ratios) | 1.135 (0.960–1.342) |
| Meta-analysis over 19 strata: fixed effect | 1.144 (1.101–1.189)** |
| Meta-analysis: random effects | 1.134 (1.079–1.192)** |
| Meta-analysis: equal weight per stratum | 1.106 (1.041–1.176)** |

Heterogeneity across strata: Q 25.2 on 18 df (p 0.118), I² 29%, tau 0.056 (log rate ratio).

| Stratum | Records | Rate ratio per SD (state FE) |
| --- | --- | --- |
| Blue Book 1950s | 659 | 0.909 (0.730–1.133) |
| Blue Book 1960s | 335 | 0.957 (0.636–1.440) |
| Hatch 1950s | 1,830 | 0.991 (0.812–1.209) |
| Hatch 1960s | 875 | 0.890 (0.646–1.227) |
| Hatch 1970s | 1,049 | 0.987 (0.817–1.191) |
| Hatch 1980s | 572 | 1.190 (0.861–1.644) |
| Hatch 1990s | 711 | 1.347 (1.008–1.800)* |
| NICAP 1950s | 505 | 1.046 (0.761–1.436) |
| NICAP 1960s | 538 | 1.037 (0.833–1.291) |
| NICAP 1970s | 335 | 0.898 (0.687–1.174) |
| NICAP 1980s | 143 | 1.241 (0.876–1.760) |
| NUFORC 1950s | 307 | 1.321 (1.010–1.728)* |
| NUFORC 1960s | 912 | 1.241 (1.030–1.495)* |
| NUFORC 1970s | 1,677 | 1.140 (0.983–1.321) |
| NUFORC 1980s | 1,427 | 1.278 (1.114–1.468)** |
| NUFORC 1990s | 5,794 | 1.224 (1.089–1.377)** |
| NUFORC 2000s | 22,881 | 1.218 (1.089–1.362)** |
| NUFORC 2010s | 39,742 | 1.184 (1.076–1.304)** |
| NUFORC 2020s | 8,158 | 1.101 (0.998–1.214) |

## Carbonate share (all eras)

| Model | Rate ratio per SD |
| --- | --- |
| All strata, natural weighting | 1.078 (1.034–1.123)** |
| All strata, balanced weighting | 1.034 (0.950–1.126) |
| Before 1980 (all catalogs) | 1.035 (0.950–1.128) |
| From 1980 (all catalogs) | 1.083 (1.036–1.133)** |
| Difference, from 1980 vs before (ratio of ratios) | 1.047 (0.952–1.151) |
| Same decades (1950s, 1960s, 1970s, 1980s, 1990s): Hatch | 1.006 (0.934–1.084) |
| Same decades: NUFORC | 1.044 (0.992–1.098) |
| Same decades: NUFORC vs Hatch (ratio of ratios) | 1.037 (0.953–1.129) |
| Meta-analysis over 19 strata: fixed effect | 1.062 (1.040–1.084)** |
| Meta-analysis: random effects | 1.059 (1.036–1.083)** |
| Meta-analysis: equal weight per stratum | 1.031 (0.992–1.073) |

Heterogeneity across strata: Q 19.1 on 18 df (p 0.385), I² 6%, tau 0.012 (log rate ratio).

| Stratum | Records | Rate ratio per SD (state FE) |
| --- | --- | --- |
| Blue Book 1950s | 659 | 1.076 (0.839–1.379) |
| Blue Book 1960s | 335 | 1.188 (1.003–1.407)* |
| Hatch 1950s | 1,830 | 1.101 (0.989–1.226) |
| Hatch 1960s | 875 | 1.019 (0.881–1.180) |
| Hatch 1970s | 1,049 | 0.996 (0.912–1.088) |
| Hatch 1980s | 572 | 0.902 (0.723–1.125) |
| Hatch 1990s | 711 | 0.995 (0.761–1.299) |
| NICAP 1950s | 505 | 1.036 (0.829–1.295) |
| NICAP 1960s | 538 | 1.057 (0.905–1.234) |
| NICAP 1970s | 335 | 1.026 (0.828–1.273) |
| NICAP 1980s | 143 | 0.903 (0.664–1.228) |
| NUFORC 1950s | 307 | 0.992 (0.811–1.214) |
| NUFORC 1960s | 912 | 0.965 (0.868–1.072) |
| NUFORC 1970s | 1,677 | 0.983 (0.895–1.079) |
| NUFORC 1980s | 1,427 | 1.100 (1.017–1.190)* |
| NUFORC 1990s | 5,794 | 1.053 (1.004–1.105)* |
| NUFORC 2000s | 22,881 | 1.062 (1.002–1.125)* |
| NUFORC 2010s | 39,742 | 1.107 (1.062–1.154)** |
| NUFORC 2020s | 8,158 | 1.078 (1.002–1.159)* |

Descriptive and post hoc. Counts describe reporting and collection, not phenomena. Controls are today's values; Blue Book's index and unknowns are one catalog here.
