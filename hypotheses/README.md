# Hypotheses

One YAML file per pre-registered hypothesis. A file is written and committed **before** the
hypothesis touches confirmation data; the commit timestamp is the registration record.

Rules:

- Registered files are never edited. A changed hypothesis gets a new ID.
- Exploration years (2001-2010) are for pipeline checks and power estimates only, not tuning.
- Every confirmation run is recorded in `results/`, including nulls and underpowered results.
- Explanation filters are defined in `configs/filters.yaml`; a hypothesis lists in
  `filters_disabled` any rule that keys on its own exposure.

| ID | Title | Status |
| --- | --- | --- |
| H-geo-01 | Geophysical triggers (Persinger) | registered 2026-11-11 |
| H-launch-01 | Rocket launches seen at twilight | registered 2026-11-11 |
| H-celebrate-01 | Celebration nights | registered 2026-11-11 |
| H-persist-01 | Persistent county hotspots | registered 2026-11-11 |
| H-install-01 | Proximity to military installations | registered 2026-11-11 |
| H-volcano-01 | Proximity to young volcanoes | registered 2026-11-11 |
| H-rockage-01 | Geologic age of surface rock | registered 2026-11-19 |
| H-rocktype-01 | Rock type at the surface (screen of seven classes) | registered 2026-11-19 |
| H-anomaly-01 | Structure in high-strangeness residual reports | draft; not run (known-cause gate failed) |

Registration dates are those in `registry.yaml` (the commit that recorded the spec, implementation and filter
hashes).

Post-hoc analyses (not registered; descriptive):

| ID | Title | Status |
| --- | --- | --- |
| H-rockera-01 | Surface rock era as a class (NUFORC) | post hoc 2026-11-19 |
| H-hatchpal-01 | Paleozoic surface rock in the Hatch catalog, 1950-1999 | post hoc 2026-11-22 (drafted for registration; confirm years used by the all-catalog run) |
