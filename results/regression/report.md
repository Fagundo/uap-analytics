# Regression check

Each committed result rerun from the current code and data and compared value by value (relative tolerance 1e-5; run metadata ignored). A raw file that differs from the one the baseline used is listed as a warning; the split still passes when every value matches.

| Hypothesis | Split | Compared with | Result | Values differing | New fields | Inputs | Raw files changed | Minutes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H-celebrate-01 | confirm | baseline | same | 0 | 0 | match | 0 | 0.2 |
| H-celebrate-01 | explore | baseline | same | 0 | 0 | match | 0 | 0.1 |
| H-geo-01 | confirm | baseline | same | 0 | 0 | match | 0 | 0.3 |
| H-geo-01 | explore | baseline | same | 0 | 0 | match | 0 | 0.3 |
| H-install-01 | confirm | baseline | CHANGED | 8 | 0 | match | 1 | 4.2 |
| H-install-01 | explore | baseline | CHANGED | 4 | 0 | match | 1 | 4.1 |
| H-launch-01 | confirm | baseline | same | 0 | 0 | match | 0 | 0.5 |
| H-launch-01 | explore | baseline | same | 0 | 0 | match | 0 | 0.4 |
| H-persist-01 | confirm | baseline | CHANGED | 8 | 0 | match | 1 | 0.9 |
| H-persist-01 | explore | baseline | CHANGED | 1 | 0 | match | 1 | 0.9 |
| H-rockage-01 | confirm | baseline | CHANGED | 15 | 0 | match | 1 | 41.5 |
| H-rockage-01 | explore | baseline | CHANGED | 13 | 0 | match | 1 | 4.3 |
| H-rockage-01 | holdout | baseline | CHANGED | 14 | 0 | match | 1 | 4.4 |
| H-rockera-01 | explore | baseline | same | 0 | 0 | match | 0 | 19.1 |
| H-rocktype-01 | confirm | baseline | same | 0 | 0 | match | 0 | 15.4 |
| H-rocktype-01 | explore | baseline | same | 0 | 0 | match | 0 | 15.6 |
| H-rocktype-01 | holdout | baseline | same | 0 | 0 | match | 0 | 16.1 |
| H-volcano-01 | confirm | baseline | same | 0 | 0 | match | 0 | 2.2 |
| H-volcano-01 | explore | baseline | same | 0 | 0 | match | 0 | 2.1 |

## H-install-01 confirm

- raw input changed: data/raw/airports/airports.csv
- tests.proximity.p_bh: committed 0.38410689438659484, now 0.38415441289243724
- tests.proximity.power: committed 0.6000768104362868, now 0.6000674882081849
- tests.proximity.tiers.all.terms[0].p_value: committed 0.4411775501154169, now 0.44122506151081375
- tests.proximity.tiers.filtered.terms[0].p_value: committed 0.38410689438659484, now 0.38415441289243724
- tests.proximity.tiers.high_quality.terms[0].ci_high: committed 1.0834487343964279, now 1.0834613620614844
- tests.proximity.tiers.high_quality.terms[0].ci_low: committed 0.9716974504249135, now 0.9717100654319466
- tests.proximity.tiers.high_quality.terms[0].p_value: committed 0.35438338321166474, now 0.3541470643893295
- tests.proximity.tiers.high_quality.terms[0].rate_ratio: committed 1.0260528119347017, now 1.0260654516266257

## H-install-01 explore

- raw input changed: data/raw/airports/airports.csv
- tests.proximity.p_bh: committed 0.7332393584617548, now 0.7331937269333964
- tests.proximity.tiers.all.terms[0].p_value: committed 0.7575443241717326, now 0.7575292332949036
- tests.proximity.tiers.filtered.terms[0].p_value: committed 0.7332393584617548, now 0.7331937269333964
- tests.proximity.tiers.high_quality.terms[0].p_value: committed 0.558968742012619, now 0.5587895480377594

## H-persist-01 confirm

- raw input changed: data/raw/airports/airports.csv
- tests.persistence.checks.local.rate_ratio: committed 1.1885280944967342, now 1.1885474837014762
- tests.persistence.checks.reporting_propensity.rate_ratio: committed 1.1784903881520512, now 1.1785045876381623
- tests.persistence.tiers.all.terms[0].ci_high: committed 1.2378057703662304, now 1.2378250643511675
- tests.persistence.tiers.all.terms[0].ci_low: committed 1.1539140045947438, now 1.1539315780809527
- tests.persistence.tiers.all.terms[0].rate_ratio: committed 1.19512401590537, now 1.19514243079848
- tests.persistence.tiers.filtered.terms[0].ci_high: committed 1.2353260859213373, now 1.235344820793879
- tests.persistence.tiers.filtered.terms[0].ci_low: committed 1.150535973120448, now 1.1505529075173722
- tests.persistence.tiers.filtered.terms[0].rate_ratio: committed 1.1921774617843521, now 1.1921952756788312

## H-persist-01 explore

- raw input changed: data/raw/airports/airports.csv
- tests.persistence.tiers.filtered.terms[0].ci_high: committed 1.185184003985318, now 1.1851959642245324

## H-rockage-01 confirm

- raw input changed: data/raw/airports/airports.csv
- tests.age.checks.shift_test.rate_ratio: committed 0.9934692635352242, now 0.9934371292353107
- tests.age.p_bh: committed 0.8676065423997005, now 0.866985948767748
- tests.age.power: committed 0.9628240828998799, now 0.9628014273418073
- tests.age.tiers.all.terms[0].ci_high: committed 1.0782668570863492, now 1.0782479447276934
- tests.age.tiers.all.terms[0].ci_low: committed 0.9256689902338728, now 0.9256226934121662
- tests.age.tiers.all.terms[0].p_value: committed 0.9806983846474026, now 0.9800105193787977
- tests.age.tiers.all.terms[0].rate_ratio: committed 0.9990586533341136, now 0.9990249079802664
- tests.age.tiers.filtered.terms[0].ci_high: committed 1.073028067729952, now 1.0730102452386057
- tests.age.tiers.filtered.terms[0].ci_low: committed 0.919809282973587, now 0.9197650573446614
- tests.age.tiers.filtered.terms[0].p_value: committed 0.8676065423997005, now 0.866985948767748
- tests.age.tiers.filtered.terms[0].rate_ratio: committed 0.9934692635352242, now 0.9934371292353107
- tests.age.tiers.high_quality.terms[0].ci_high: committed 1.0807349265623614, now 1.0807130999189403
- tests.age.tiers.high_quality.terms[0].ci_low: committed 0.9166228917105559, now 0.9165875836988324
- tests.age.tiers.high_quality.terms[0].p_value: committed 0.9107648185064938, now 0.91022076357688
- tests.age.tiers.high_quality.terms[0].rate_ratio: committed 0.9953021518906643, now 0.9952729318766669

## H-rockage-01 explore

- raw input changed: data/raw/airports/airports.csv
- tests.age.checks.shift_test.rate_ratio: committed 1.0414863791454378, now 1.0414731088594127
- tests.age.p_bh: committed 0.21831817772172102, now 0.21849684257222723
- tests.age.power: committed 0.8228847225404421, now 0.8228288551965965
- tests.age.tiers.all.terms[0].ci_low: committed 0.9766261276008886, now 0.9766074172792809
- tests.age.tiers.all.terms[0].p_value: committed 0.19900678332749333, now 0.19918027628518675
- tests.age.tiers.all.terms[0].rate_ratio: committed 1.0459914946044504, now 1.0459769021624135
- tests.age.tiers.filtered.terms[0].ci_low: committed 0.97621689181268, now 0.976199745261608
- tests.age.tiers.filtered.terms[0].p_value: committed 0.21831817772172102, now 0.21849684257222723
- tests.age.tiers.filtered.terms[0].rate_ratio: committed 1.0414863791454378, now 1.0414731088594127
- tests.age.tiers.high_quality.terms[0].ci_high: committed 1.1139571603241205, now 1.1139457250791103
- tests.age.tiers.high_quality.terms[0].ci_low: committed 0.9693642732363686, now 0.9693526342946904
- tests.age.tiers.high_quality.terms[0].p_value: committed 0.27893757522721374, now 0.27908302625082815
- tests.age.tiers.high_quality.terms[0].rate_ratio: committed 1.039148821456311, now 1.0391372493885227

## H-rockage-01 holdout

- raw input changed: data/raw/airports/airports.csv
- tests.age.checks.shift_test.rate_ratio: committed 1.0567443055487065, now 1.0567213792596477
- tests.age.p_bh: committed 0.2698293737933348, now 0.27003964920726686
- tests.age.power: committed 0.2310896604927572, now 0.2310622123633604
- tests.age.tiers.all.terms[0].ci_high: committed 1.1648311327696756, now 1.1648112507581094
- tests.age.tiers.all.terms[0].ci_low: committed 0.9521945469802895, now 0.9521689869924179
- tests.age.tiers.all.terms[0].p_value: committed 0.3137914479775701, now 0.31402009337126824
- tests.age.tiers.all.terms[0].rate_ratio: committed 1.0531599369403295, now 1.053136813843159
- tests.age.tiers.filtered.terms[0].ci_high: committed 1.165588934928541, now 1.1655688861475606
- tests.age.tiers.filtered.terms[0].ci_low: committed 0.9580637683199009, now 0.9580386767831442
- tests.age.tiers.filtered.terms[0].p_value: committed 0.2698293737933348, now 0.27003964920726686
- tests.age.tiers.filtered.terms[0].rate_ratio: committed 1.0567443055487065, now 1.0567213792596477
- tests.age.tiers.high_quality.terms[0].ci_low: committed 1.014552533589033, now 1.0145160221581095
- tests.age.tiers.high_quality.terms[0].p_value: committed 0.030969477137782794, now 0.031009204462976846
- tests.age.tiers.high_quality.terms[0].rate_ratio: committed 1.1709599192193527, now 1.170933235569965
