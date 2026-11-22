# Post hoc: geology on every catalog, 1950–2023, with time fixed effects

Exploratory and labelled post hoc: it uses the Hatch 1960-1999 records, so H-hatchpal-01 can no longer be a
confirmation. Quick models only (no shift test).

Data: one row per county x decade (1950s ... 2020s, the last 2020-2023). Records: every source in the export
(NUFORC, Hatch, NICAP, Blue Book unknowns and index, PURSUE's incidents, Magonia), contiguous U.S., placed at
site or town level, not a hoax, not a NUFORC repeat, not explained at high confidence by uap-data's flags; one
per cross-source duplicate group in the combined set. Offset: the county's population at the decade's census
(1950-1990 from the Census 1900-1990 counts, 2000 and 2010 from the Census API, the 2020s from today's
estimates) x days in the decade. Controls: the H-persist-01 set (today's values). Standard errors clustered by
state (counties repeat across decades).

Time is handled three ways, side by side:
  cross-section   records summed over 1950-2023 per county, state fixed effects (as the registered studies)
  state + decade  panel with state and decade fixed effects (decade-wide swings in reporting removed)
  state x decade  panel with one effect per state per decade (each county compared with its own state's
                  counties in the same decade; regional reporting shifts over time removed too)
County fixed effects cannot be used: geology does not change over time, so they would absorb it.

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
| combined: one per cross-source duplicate group | 88,659 |

By source (before combining): nuforc 80,971, hatch 6,531, nicap 1,949, bluebook-index 695, bluebook-unknowns 315, pursue 141, magonia 181.

## Rate ratio per SD (95% CI); * p < 0.05, ** p < 0.01

### Paleozoic share

| Data | Records | Cross-section, state FE | Panel, state + decade FE | Panel, state x decade FE |
| --- | --- | --- | --- | --- |
| combined | 88,659 | 1.126 (1.042–1.218)** | failed (ValueError) | failed (ValueError) |
| nuforc | 80,971 | 1.154 (1.064–1.252)** | failed (ValueError) | failed (ValueError) |
| hatch | 6,531 | 0.964 (0.872–1.065) | failed (ValueError) | failed (ValueError) |
| nicap | 1,949 | 0.923 (0.770–1.106) | failed (ValueError) | failed (ValueError) |
| bluebook-index | 695 | 0.796 (0.576–1.100) | failed (ValueError) | failed (ValueError) |
| bluebook-unknowns | 315 | 0.998 (0.780–1.276) | failed (ValueError) | failed (ValueError) |
| pursue | 141 | (too few records) | | |
| magonia | 181 | (too few records) | | |

### Carbonate share (all eras)

| Data | Records | Cross-section, state FE | Panel, state + decade FE | Panel, state x decade FE |
| --- | --- | --- | --- | --- |
| combined | 88,659 | 1.079 (1.034–1.126)** | failed (ValueError) | failed (ValueError) |
| nuforc | 80,971 | 1.090 (1.041–1.142)** | failed (ValueError) | failed (ValueError) |
| hatch | 6,531 | 0.989 (0.939–1.043) | failed (ValueError) | failed (ValueError) |
| nicap | 1,949 | 0.940 (0.820–1.078) | failed (ValueError) | failed (ValueError) |
| bluebook-index | 695 | 0.976 (0.755–1.262) | failed (ValueError) | failed (ValueError) |
| bluebook-unknowns | 315 | 0.937 (0.752–1.168) | failed (ValueError) | failed (ValueError) |
| pursue | 141 | (too few records) | | |
| magonia | 181 | (too few records) | | |

## Combined data by decade (cross-section within the decade, state FE)

| Decade | Records | Paleozoic share | Carbonate share |
| --- | --- | --- | --- |
| 1950s | 3,386 | 0.968 (0.826–1.135) | 1.034 (0.954–1.120) |
| 1960s | 2,712 | 1.016 (0.874–1.180) | 0.991 (0.895–1.097) |
| 1970s | 3,063 | 0.997 (0.908–1.094) | 0.970 (0.914–1.030) |
| 1980s | 2,142 | 1.203 (1.083–1.336)** | 1.052 (0.966–1.147) |
| 1990s | 6,534 | 1.197 (1.103–1.300)** | 1.052 (0.995–1.114) |
| 2000s | 22,909 | 1.129 (1.056–1.207)** | 1.046 (1.003–1.090)* |
| 2010s | 39,744 | 1.133 (1.057–1.214)** | 1.078 (1.046–1.110)** |
| 2020s | 8,169 | 1.086 (1.010–1.168)* | 1.073 (1.001–1.151)* |

Descriptive and post hoc. Counts describe reporting and collection, not phenomena; the catalogs overlap (Hatch drew on NICAP and Blue Book), so the per-source rows are not independent.
