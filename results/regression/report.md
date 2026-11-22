# Regression check

Each committed result rerun from the current code and data and compared value by value (relative tolerance 1e-5; run metadata ignored). A raw file that differs from the one the baseline used is listed as a warning; the split still passes when every value matches.

| Hypothesis | Split | Compared with | Result | Values differing | New fields | Inputs | Raw files changed | Minutes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H-celebrate-01 | confirm | baseline | same | 0 | 0 | match | 0 | 0.2 |
| H-celebrate-01 | explore | baseline | same | 0 | 0 | match | 0 | 0.1 |
| H-geo-01 | confirm | baseline | same | 0 | 0 | match | 0 | 0.2 |
| H-geo-01 | explore | baseline | same | 0 | 0 | match | 0 | 0.2 |
| H-install-01 | confirm | baseline | same, raw differs | 0 | 0 | match | 1 | 4.9 |
| H-install-01 | explore | baseline | same, raw differs | 0 | 0 | match | 1 | 4.1 |
| H-launch-01 | confirm | baseline | same | 0 | 0 | match | 0 | 0.7 |
| H-launch-01 | explore | baseline | same | 0 | 0 | match | 0 | 0.6 |
| H-persist-01 | confirm | baseline | same | 0 | 0 | match | 0 | 1.4 |
| H-persist-01 | explore | baseline | same | 0 | 0 | match | 0 | 1.4 |
| H-rockage-01 | confirm | baseline | same, raw differs | 0 | 0 | match | 1 | 42.9 |
| H-rockage-01 | explore | baseline | same, raw differs | 0 | 0 | match | 1 | 5.4 |
| H-rockage-01 | holdout | baseline | same, raw differs | 0 | 0 | match | 1 | 5.4 |
| H-rockera-01 | explore | baseline | same | 0 | 0 | match | 0 | 22.9 |
| H-rocktype-01 | confirm | baseline | same | 0 | 0 | match | 0 | 16.8 |
| H-rocktype-01 | explore | baseline | same | 0 | 0 | match | 0 | 17.1 |
| H-rocktype-01 | holdout | baseline | same | 0 | 0 | match | 0 | 17.6 |
| H-volcano-01 | confirm | baseline | same | 0 | 0 | match | 0 | 3.5 |
| H-volcano-01 | explore | baseline | same | 0 | 0 | match | 0 | 3.3 |

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
