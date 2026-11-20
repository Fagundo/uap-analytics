# H-rockera-01 diagnostic: Paleozoic share with land-use controls (post hoc)

Pooled 2001–2023, filtered tier, H-persist-01 controls, state fixed effects, state-clustered SEs. Land cover: NLCD 2011 shares per county (480 m cells): developed, forest, shrub/grass, pasture, cropland, wetland (water and barren are the reference). Sediment cover: share of the county's surface mapped as unconsolidated deposits, any era (SGMC). Descriptive only.

| Model | Paleozoic share (per SD) | p |
| --- | --- | --- |
| Paleozoic alone | 1.106 (1.046–1.169) | 0.000422 |
| + land cover | 1.132 (1.063–1.206) | 0.00012 |
| + sediment cover | 1.100 (1.034–1.172) | 0.00278 |
| + land cover + sediment cover | 1.107 (1.039–1.180) | 0.00165 |

## Control terms in the full model (per SD)

| Term | Rate ratio | p |
| --- | --- | --- |
| lc_developed | 1.005 (0.876–1.154) | 0.941 |
| lc_forest | 0.771 (0.633–0.938) | 0.00931 |
| lc_shrub_grass | 0.908 (0.728–1.132) | 0.389 |
| lc_pasture | 0.890 (0.809–0.978) | 0.0156 |
| lc_cropland | 0.783 (0.641–0.956) | 0.0163 |
| lc_wetland | 0.973 (0.869–1.088) | 0.626 |
| share_unconsolidated_all | 0.943 (0.888–1.001) | 0.0528 |

Correlation of Paleozoic share with the controls (all counties): lc_developed +0.09, lc_forest +0.25, lc_shrub_grass -0.38, lc_pasture +0.33, lc_cropland +0.09, lc_wetland -0.30, share_unconsolidated_all -0.56.

## Full model by period

| Period | Paleozoic share (per SD) | p |
| --- | --- | --- |
| 2001–2010 | 1.099 (1.034–1.168) | 0.00238 |
| 2011–2020 | 1.142 (1.066–1.222) | 0.000148 |
| 2021–2023 | 1.008 (0.926–1.097) | 0.849 |

## Leave one state out (full model)

Rate ratio ranges 1.088 (without 55) to 1.128 (without 13); p < 0.05 in 49 of 49 fits; largest p 0.00636 (without 51). FIPS codes: lowest 55, highest 13.

## Shift test (full model)

Real map 1.107; 200 shifted copies fitted, rate ratios 0.942 (2.5%), 1.023 (median), 1.097 (97.5%); two-sided p 0.015.
