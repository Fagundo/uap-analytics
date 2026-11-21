# Reading data from PURSUE (data refactor, Phase 4)

PURSUE loads, cleans, enriches and stores UAP data; uap-geo analyses it. uap-geo reads PURSUE's combined
export, never PURSUE's code (`tests/test_pursue_export.py::test_import_boundary`).

* **Pin**: `configs/pursue_export.yaml` names one release of the private `Fagundo/PURSUE` repository
  (`export-<content version>`) and the SHA-256 of its two assets. `use: true` makes it the source of NUFORC
  reports, GCAT launches, Kp and M3.0+ quakes; `UAP_GEO_DATA=legacy|export` overrides it for one run.
* **Access**: a fine-grained token with read-only Contents access to `Fagundo/PURSUE`, stored as the Actions
  secret `PURSUE_EXPORT_TOKEN` (locally: the same variable, or `GH_TOKEN`).
* **Reader**: `src/uap_geo/data/scraping/pursue_export.py`. `ExportTables` returns the tables uap-geo's own
  loaders returned (the cleaned NUFORC reports in source order with their cleaning counts, launches, daily Kp,
  quakes), so analysis code is unchanged; `SourceRegistry` picks the export or the old loader.
* **Gate**: `uap-geo regression export-check` (workflow *export check*) compares every table with the old
  loader on the pinned raw files; then the regression workflow, reading the export, must reproduce every
  registered result. Only after both does the old loading code go.
* **Restricted data**: the restricted tier (NUFORC rows with text) is extracted under `data/raw/pursue_export/`
  (gitignored) and never committed; `tests/test_licence_leak.py` guards committed tables.
