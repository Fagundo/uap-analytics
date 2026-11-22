# Reading data from PURSUE (data refactor, Phase 4)

PURSUE loads, cleans, enriches and stores UAP data; uap-geo analyses it. uap-geo reads PURSUE's combined
export, never PURSUE's code (`tests/test_pursue_export.py::test_import_boundary`).

* **Pin**: `configs/pursue_export.yaml` names one release of the private `Fagundo/uap-data` repository
  (`export-<content version>`) and the SHA-256 of its two assets. It is the only source of NUFORC reports,
  GCAT launches, Kp, M3.0+ quakes and the residual set's explanation flags. (The v1 county pipeline's M2.5
  quakes still come from uap-geo's own ComCat loader until PURSUE's quake layer covers them.)
* **Access**: a fine-grained token with read-only Contents access to `Fagundo/uap-data`, stored as the Actions
  secret `PURSUE_EXPORT_TOKEN` (locally: the same variable, or `GH_TOKEN`).
* **Reader**: `src/uap_geo/data/scraping/pursue_export.py`. `ExportTables` returns the tables uap-geo's own
  loaders returned (the cleaned NUFORC reports in source order with their cleaning counts, launches, daily Kp,
  quakes), so analysis code is unchanged; `SourceRegistry` picks the export or the old loader.
* **Gate (passed)**: every table matched the old loader on the pinned raw files
  (`results/regression/export_check.json`), and the regression workflow, reading the export, reproduced all
  19 registered results. The old NUFORC, GCAT and Kp loaders, the NUFORC cleaner, the residual checks other
  than the LLM gate's launch window, the planet ephemeris and the parity-reference tools were then deleted;
  their committed references (`results/regression/*_reference.json`) stay as records.
* **Restricted data**: the restricted tier (NUFORC rows with text) is extracted under `data/raw/pursue_export/`
  (gitignored) and never committed; `tests/test_licence_leak.py` guards committed tables.
