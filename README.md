# uap-analytics

Statistical tests of UAP reports: where and when people report, what explains the reports, and whether
anything is left once the ordinary explanations are taken out. Every test here reads one versioned data
export; nothing in this repository fetches or cleans sighting records itself.

- **Pre-registered hypotheses.** Each test is written down and committed before it sees its confirmation
  years, with explore / confirm / holdout splits; post-hoc analyses are labelled as such and give no verdicts.
- **Replications.** Analyses first run in the data repository (flight programs, nuclear tests, Blue Book,
  document networks, topics, claim checks), ported here and checked number for number against the originals.
- **The v1 county study.** Do reports cluster around geologic or environmental features beyond observer
  opportunity? It extends [Medina, Brewer & Kirkpatrick (2023), *Scientific Reports*](https://doi.org/10.1038/s41598-023-49527-x).

Results so far: [`docs/RESULTS.md`](docs/RESULTS.md) (v1), [`hypotheses/README.md`](hypotheses/README.md)
(every registered and post-hoc test), [`results/`](results/) (one folder per hypothesis and split).

## Where the data comes from

Sightings (NUFORC, Hatch, NICAP, Blue Book, Magonia and incidents from the released government documents),
their enrichment (explanation flags, sky and launch context), context layers (rocket launches, Kp,
earthquakes, holidays, flight programs, nuclear tests) and the document entity graph all come from the data
repository's **combined export**, a versioned release pinned in
[`configs/pursue_export.yaml`](configs/pursue_export.yaml) by tag and SHA-256 (format:
[`docs/PURSUE_EXPORT.md`](docs/PURSUE_EXPORT.md)). Reading it needs the `PURSUE_EXPORT_TOKEN` secret.

The export has two tiers. NUFORC records and narrative text from copyrighted catalogs are **restricted**:
analyses may use them, but only aggregates are committed or published here (`tests/test_licence_leak.py`
checks). `src/uap_geo/data/scraping/pursue_export.py` is the only reader of sighting data, and an
import-boundary test keeps this repository from importing the data repository's code.

County map layers (geology, land cover, census population, light pollution, terrain, airports, ...) are
built here from their public sources ([`configs/v1.yaml`](configs/v1.yaml)).

## Pre-registered hypotheses

| ID | Test | Verdict (confirm period) |
| --- | --- | --- |
| H-launch-01 | Rocket launches seen at twilight (positive control) | Confirmed: 2.18 (1.90–2.49) |
| H-celebrate-01 | Fourth of July and New Year's Eve nights | Confirmed: 2.48 and 1.80 |
| H-persist-01 | County hotspots persist from one decade to the next | Confirmed: 1.19 per SD |
| H-rocktype-01 | Carbonate (limestone, dolostone) surface rock, 1 of 7 classes | Confirmed: 1.062 per SD |
| H-geo-01 | Geomagnetic storms; earthquakes | Storms refuted; quakes underpowered |
| H-install-01 | Closeness to military installations | Inconclusive |
| H-volcano-01 | Closeness to young volcanoes | Underpowered |
| H-rockage-01 | Geologic age of surface rock | Refuted |
| H-anomaly-01 | Structure in high-strangeness residual reports | Not run: its known-cause gate failed |

Post hoc (no verdicts): H-rockera-01 (Paleozoic terrain, 1.106 per SD, beats all shifted maps) and
H-hatchpal-01 (the same across catalogs, 1950–2023: the association follows modern reporting through NUFORC
rather than the years of the events). Rules and specs: [`hypotheses/`](hypotheses/).

## Replications

`src/uap_geo/replications/` holds the analyses first run in the data repository, ported unchanged and read from
the export:

| Name | Question |
| --- | --- |
| `programs` | Do sightings cluster near classified flight programs in space and time? (shuffle tests) |
| `nuclear` | Do reports rise in the days after nuclear tests, at each test site? |
| `bluebook` | Did Blue Book's conclusions shift when the spy planes began flying, and where? |
| `networks` | Who writes to whom in the released documents; which names cluster beyond chance? |
| `topics` | Topics and themes in the documents, and how they differ by era and agency |
| `claims` | Do the explanations offered for famous cases fit their own stated facts? |

Each was checked against the original outputs before the code left the data repository
([`tests/parity/`](tests/parity/); 0 differences across about 14,800 values). Aggregates are committed under
`results/replications/`; the full outputs of the document analyses (networks, topics, claims: government
documents only) are published as release `replications-<export tag>`, which the data repository's explorer
and event dossier read.

## Run it

GitHub Actions (the data and caches live there):

- **study**: `hypothesis run|diagnose <ID> ...` for one hypothesis.
- **regression**: reruns every committed result and compares it value by value with its baseline (relative
  tolerance 1e-5). Live raw inputs (airports, earthquakes, launches, Kp, volcanoes, Census estimates) are
  seeded from release `pinned-raw-inputs-v2` so upstream changes cannot move a result; see
  [`results/regression/BASELINE.md`](results/regression/BASELINE.md).
- **replications**: runs the replications, checks parity, publishes the document-analysis outputs.
- **v1 analysis**: the original county study (`ingest build analyze`).

Locally (needs the export token for sighting data):

```bash
uv sync --group dev
uv run pytest
uv run uap-geo hypothesis run H-rocktype-01 --split explore
uv run uap-geo hypothesis diagnose H-hatchpal-01 --diagnostic stacked
uv run uap-geo replicate programs nuclear bluebook
uv run uap-geo regression run --only H-persist-01
```

## Layout

```
src/uap_geo/
├── common/          config, downloads, CRS constants, base classes
├── data/
│   ├── scraping/    pursue_export.py (the one reader of sighting data), map-layer sources, SourceRegistry
│   ├── io/          Parquet / GeoParquet table store
│   └── preprocessing/
├── features/        county covariates (CovariateBuilder subclasses)
├── hypotheses/      one study class per hypothesis, designs, diagnostics
├── replications/    programs, nuclear, bluebook, networks, topics, claims; inputs.py reads the export
├── regression/      rerun-and-compare, input fingerprints, pinned raw inputs
├── residual/, llm/, audit/, classify/, events/, cube/   residual set, LLM features, sensitivity checks
├── training/, evaluation/, reporting/   negative binomial models, shift tests, Gi*, Moran's I, report writers
├── pipeline.py      the v1 county study
└── cli.py           `uap-geo`
hypotheses/          specs (YAML), registry with spec/implementation/filter hashes
results/             one folder per hypothesis and split; regression; replications
configs/             sources, filters, the export pin
```

## Limitations

- Reports are self-selected and unverified: results describe **reporting**, not phenomena.
- NUFORC's public extract stops in 2023 and holds about 71% of the reports the 2023 paper used for 2001–2020.
- Coordinates are town-level at best, so the county is the finest honest grain for rate models.
- Residual spatial clustering remains, so ordinary p-values are optimistic; shift tests and held-out years
  carry the conclusions. See [`docs/ROBUSTNESS.md`](docs/ROBUSTNESS.md).
