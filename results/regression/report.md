# Regression check

Each committed result rerun from the current code and data and compared value by value (relative tolerance 1e-6; run metadata ignored).

| Hypothesis | Split | Compared with | Result | Values differing | New fields | Inputs | Raw files changed | Minutes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H-celebrate-01 | confirm | baseline | same | 0 | 0 | match | 0 | 0.2 |
| H-celebrate-01 | explore | baseline | same | 0 | 0 | match | 0 | 0.2 |
| H-geo-01 | confirm | baseline | CHANGED | 1 | 0 | match | 2 | 0.9 |
| H-geo-01 | explore | baseline | CHANGED | 0 | 0 | match | 2 | 0.4 |
| H-install-01 | confirm | baseline | same | 0 | 0 | match | 0 | 4.2 |
| H-install-01 | explore | baseline | same | 0 | 0 | match | 0 | 4.1 |
| H-launch-01 | confirm | baseline | same | 0 | 0 | match | 0 | 0.5 |
| H-launch-01 | explore | baseline | same | 0 | 0 | match | 0 | 0.5 |
| H-persist-01 | confirm | baseline | same | 0 | 0 | match | 0 | 1.1 |
| H-persist-01 | explore | baseline | same | 0 | 0 | match | 0 | 1.1 |
| H-rockage-01 | confirm | baseline | same | 0 | 0 | match | 0 | 4.8 |
| H-rockage-01 | explore | baseline | same | 0 | 0 | match | 0 | 4.8 |
| H-rockage-01 | holdout | baseline | same | 0 | 0 | match | 0 | 4.9 |
| H-rockera-01 | explore | baseline | same | 0 | 0 | match | 0 | 27.9 |
| H-rocktype-01 | confirm | baseline | same | 0 | 0 | match | 0 | 15.6 |
| H-rocktype-01 | explore | baseline | same | 0 | 0 | match | 0 | 15.8 |
| H-rocktype-01 | holdout | baseline | same | 0 | 0 | match | 0 | 16.2 |
| H-volcano-01 | confirm | baseline | CHANGED | 0 | 0 | match | 1 | 3.5 |
| H-volcano-01 | explore | baseline | CHANGED | 0 | 0 | match | 1 | 3.3 |

## H-geo-01 confirm

- raw input changed: data/raw/earthquakes/quakes_2024_m3.csv
- raw input changed: data/raw/earthquakes/quakes_2026_m3.csv
- tests.storm.tiers.all.terms[1].p_value: committed 4.878253435809939e-07, now 4.878239931526553e-07

## H-geo-01 explore

- raw input changed: data/raw/earthquakes/quakes_2024_m3.csv
- raw input changed: data/raw/earthquakes/quakes_2026_m3.csv

## H-volcano-01 confirm

- raw input changed: data/raw/volcanoes/holocene_volcanoes.csv

## H-volcano-01 explore

- raw input changed: data/raw/volcanoes/holocene_volcanoes.csv
