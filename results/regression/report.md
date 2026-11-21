# Regression check

Each committed result rerun from the current code and data and compared value by value (relative tolerance 1e-6; run metadata ignored).

| Hypothesis | Split | Compared with | Result | Values differing | New fields | Inputs | Raw files changed | Minutes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H-celebrate-01 | confirm | baseline | same | 0 | 0 | match | 0 | 0.1 |
| H-celebrate-01 | explore | baseline | same | 0 | 0 | match | 0 | 0.1 |
| H-geo-01 | confirm | baseline | CHANGED | 1 | 0 | match | 0 | 0.2 |
| H-geo-01 | explore | baseline | same | 0 | 0 | match | 0 | 0.2 |
| H-install-01 | confirm | baseline | CHANGED | 0 | 0 | match | 1 | 5.1 |
| H-install-01 | explore | baseline | CHANGED | 0 | 0 | match | 1 | 4.0 |
| H-launch-01 | confirm | baseline | same | 0 | 0 | match | 0 | 0.5 |
| H-launch-01 | explore | baseline | same | 0 | 0 | match | 0 | 0.4 |
| H-persist-01 | confirm | baseline | same | 0 | 0 | match | 0 | 0.8 |
| H-persist-01 | explore | baseline | same | 0 | 0 | match | 0 | 0.8 |
| H-rockage-01 | confirm | baseline | CHANGED | 0 | 0 | match | 1 | 35.7 |
| H-rockage-01 | explore | baseline | CHANGED | 0 | 0 | match | 1 | 3.7 |
| H-rockage-01 | holdout | baseline | CHANGED | 0 | 0 | match | 1 | 3.8 |
| H-rockera-01 | explore | baseline | same | 0 | 0 | match | 0 | 20.0 |
| H-rocktype-01 | confirm | baseline | same | 0 | 0 | match | 0 | 12.7 |
| H-rocktype-01 | explore | baseline | same | 0 | 0 | match | 0 | 12.9 |
| H-rocktype-01 | holdout | baseline | same | 0 | 0 | match | 0 | 13.4 |
| H-volcano-01 | confirm | baseline | same | 0 | 0 | match | 0 | 2.3 |
| H-volcano-01 | explore | baseline | same | 0 | 0 | match | 0 | 2.2 |

## H-geo-01 confirm

- tests.storm.tiers.all.terms[1].p_value: committed 4.878239931526553e-07, now 4.878253435809939e-07

## H-install-01 confirm

- raw input changed: data/raw/airports/airports.csv

## H-install-01 explore

- raw input changed: data/raw/airports/airports.csv

## H-rockage-01 confirm

- raw input changed: data/raw/airports/airports.csv

## H-rockage-01 explore

- raw input changed: data/raw/airports/airports.csv

## H-rockage-01 holdout

- raw input changed: data/raw/airports/airports.csv
