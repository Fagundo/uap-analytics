# Future work

Ideas raised during analysis and parked. Each would be a new pre-registered hypothesis tested on
data not yet used for that question (for most, the 2021+ holdout or newly obtained reports).

## Launch nights beyond the rocket window (from H-launch-01)

Twilight launch nights are elevated over the whole night, not only in the 90 minutes after liftoff.
Test whether launch nights still show excess reports once reports within the launch window are
removed. Expect some residual from late filing and wrong report times, so the test needs a null
for that (for example, reports timed before liftoff on the same night).

Related: turn the launch-window match into a high-confidence filter rule (reports within 90 minutes
after a twilight launch within 1,200 km), replacing the text-only rocket rule.

## Earthquakes with refined windows (from H-geo-01 diagnostics)

The two decades disagree (see results/H-geo-01/*/diagnostics.md). A follow-up would use the quake's
local night, exclude the quake night, include M >= 3.5 for power, and needs reports from 2024 on.

## Big geomagnetic storms (from H-geo-01 diagnostics)

The Kp >= 8 hint in 2011-2020 rests on three storms and does not replicate in 2001-2010. Worth
revisiting only with reports covering the May and October 2024 storms.

## What the unexplained celebration excess is (from H-celebrate-01)

July 4 and New Year's Eve nights keep a rise of about 2.5x and 1.8x after removing lantern, fireworks
and fire-coloured-light wording. Read a sample of those reports to see what they describe
(undescribed lanterns, drones, aircraft, other), and consider a text classifier for the unexplained
tier instead of word lists.

## Persistence refinements (from H-persist-01)

The 2001-2020 watch list is still led by hotel-tourism beach counties (the seasonal-housing control
catches vacation homes, not hotel stays) and by small Virginia independent cities, whose reports are
named for the city while nearby residents are counted in the surrounding county. Next steps: a
visitor-volume control (lodging tax or hotel occupancy by county), merging Virginia independent
cities into their surrounding counties, the 2011-2020 -> 2021-2023 holdout check, and a forecasting
version that scores counties by prior excess and measures ranking accuracy on later years.

## Anomaly track (from the H-anomaly-01 gate)

The features-v1 / strangeness-v1 gate failed on the 399-report sample: launch-window reports score as
strange as the residual and are recognised as launches only 4% of the time; high strangeness is about 1%
everywhere because summaries average 88 characters. Options: full narratives (NUFORC request), or a revised
prompt and score (features-v2) checked on a fresh validation sample. Meanwhile the extractor recognises
Starlink trains (88%) and meteors (90%), so it can serve as an extra explainer for the residual set.

## Geologic age (H-rockage-01, refuted 2026-11-19)

- Power for county studies scales the explore SE by event counts; for H-rockage-01 the realised confirm SE
  (0.039) was larger than projected (0.026), so the registered 96% power is optimistic (about 68% from the
  realised SE). The confirm interval (0.920–1.073) still excludes a 10% effect either way. Base future
  county-study power on a bootstrap or simulation instead.
- Lead: the Paleozoic share of surface rock runs about 1.09 per SD in both 2001–2010 and 2011–2020
  (secondary, unadjusted, not shift-tested) and 1.06 in 2021+. Test only as a new post-hoc ID on 2024+
  reports, adding SGMC lithology to separate rock type (carbonate, shale, crystalline) from age.

## Rock type (H-rocktype-01, carbonate confirmed 2026-11-19)

- Carbonate share: 1.062 (1.034–1.090) per SD on 2011–2020, shift p 0.020; 1.058 on 2021+ (n.s.); 1.020 on
  2001–2010. Next: leave-one-state-out and drop-Florida diagnostics, karst/sinkhole density against
  carbonate share, cropland and land-use controls, and a replication on 2024+ reports.
- Cache the rock-type unit grid in its own Actions cache (each run rereads the 436 MB map, ~30 minutes).

## Era classes (H-rockera-01, post hoc 2026-11-20)

- Paleozoic share 1.106 (1.046–1.169) per SD pooled 2001–2023, beats all 200 shifted maps (p 0.005); by period
  1.10 / 1.13 / 1.04. With carbonate in the same model Paleozoic stays 1.09 and carbonate drops to 1.03 (n.s.);
  Paleozoic carbonate and non-carbonate rock both run ~1.07. The signal looks like Paleozoic terrain rather than
  carbonate. Mean log age (H-rockage-01) missed it because the pattern is not monotonic (Precambrian ~0.96).
- Confirmatory test only on 2024+ reports (new ID, Paleozoic share primary, shift test), with land-use,
  cropland and bedrock-exposure (vs glacial or coastal-plain cover) controls.
- Land-use check (2026-11-20, results/H-rockera-01/diagnostics/land_use.md): with NLCD 2011 land cover and
  sediment-cover controls the Paleozoic share stays 1.107 (1.039–1.180) pooled; leave-one-state-out 1.088–1.128,
  all p < 0.05; shift p 0.015. By period 1.099 / 1.142 / 1.008: the 2021–2023 fade is the main caution.
