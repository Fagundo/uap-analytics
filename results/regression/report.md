# Regression check

Each committed result rerun from the current code and data and compared value by value (relative tolerance 1e-5; run metadata ignored). A raw file that differs from the one the baseline used is listed as a warning; the split still passes when every value matches.

| Hypothesis | Split | Compared with | Result | Values differing | New fields | Inputs | Raw files changed | Minutes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H-celebrate-01 | confirm | registered result | same | 0 | 12 | recorded | 0 | 0.2 |
| H-celebrate-01 | explore | registered result | same | 0 | 12 | recorded | 0 | 0.1 |
| H-geo-01 | confirm | registered result | same | 0 | 6 | recorded | 0 | 0.2 |
| H-geo-01 | explore | registered result | same | 0 | 6 | recorded | 0 | 0.2 |
| H-install-01 | confirm | registered result | CHANGED | 6 | 3 | recorded | 0 | 4.2 |
| H-install-01 | explore | registered result | CHANGED | 5 | 3 | recorded | 0 | 4.1 |
| H-launch-01 | confirm | registered result | same | 0 | 3 | recorded | 0 | 0.7 |
| H-launch-01 | explore | registered result | same | 0 | 3 | recorded | 0 | 0.6 |
| H-persist-01 | confirm | registered result | CHANGED | 8 | 3 | recorded | 0 | 1.1 |
| H-persist-01 | explore | registered result | same | 0 | 3 | recorded | 0 | 1.1 |
| H-rockage-01 | confirm | registered result | CHANGED | 15 | 0 | recorded | 0 | 39.1 |
| H-rockage-01 | explore | registered result | CHANGED | 13 | 0 | recorded | 0 | 4.8 |
| H-rockage-01 | holdout | registered result | CHANGED | 14 | 0 | recorded | 0 | 4.8 |
| H-rockera-01 | explore | registered result | same | 0 | 0 | recorded | 0 | 28.2 |
| H-rocktype-01 | confirm | registered result | same | 0 | 0 | recorded | 0 | 13.9 |
| H-rocktype-01 | explore | registered result | same | 0 | 0 | recorded | 0 | 13.9 |
| H-rocktype-01 | holdout | registered result | same | 0 | 0 | recorded | 0 | 14.2 |
| H-volcano-01 | confirm | registered result | CHANGED | 15 | 3 | recorded | 0 | 2.4 |
| H-volcano-01 | explore | registered result | CHANGED | 5 | 3 | recorded | 0 | 2.2 |

## H-install-01 confirm

- tests.proximity.p_bh: committed 0.3839458194398284, now 0.38415441289243724
- tests.proximity.tiers.all.terms[0].ci_high: committed 1.0650496457949827, now 1.065036937439474
- tests.proximity.tiers.all.terms[0].p_value: committed 0.44100477079611233, now 0.44122506151081375
- tests.proximity.tiers.filtered.terms[0].ci_high: committed 1.0655833568920374, now 1.0655699059240367
- tests.proximity.tiers.filtered.terms[0].p_value: committed 0.3839458194398284, now 0.38415441289243724
- tests.proximity.tiers.high_quality.terms[0].p_value: committed 0.35426416921872694, now 0.3541470643893295

## H-install-01 explore

- tests.proximity.p_bh: committed 0.7332010934171647, now 0.7331937269333964
- tests.proximity.power: committed 0.9999999999999982, now 0.9994565943666491
- tests.proximity.tiers.all.terms[0].p_value: committed 0.7575003564446698, now 0.7575292332949036
- tests.proximity.tiers.filtered.terms[0].p_value: committed 0.7332010934171647, now 0.7331937269333964
- tests.proximity.tiers.high_quality.terms[0].p_value: committed 0.5589545044968873, now 0.5587895480377594

## H-persist-01 confirm

- tests.persistence.checks.local.rate_ratio: committed 1.1885296921712045, now 1.1885474837014762
- tests.persistence.checks.reporting_propensity.rate_ratio: committed 1.178491732101133, now 1.1785045876381623
- tests.persistence.tiers.all.terms[0].ci_high: committed 1.2378075733838139, now 1.2378250643511675
- tests.persistence.tiers.all.terms[0].ci_low: committed 1.1539155489847723, now 1.1539315780809527
- tests.persistence.tiers.all.terms[0].rate_ratio: committed 1.1951256861011281, now 1.19514243079848
- tests.persistence.tiers.filtered.terms[0].ci_high: committed 1.23532778970787, now 1.235344820793879
- tests.persistence.tiers.filtered.terms[0].ci_low: committed 1.1505372767972954, now 1.1505529075173722
- tests.persistence.tiers.filtered.terms[0].rate_ratio: committed 1.1921789593523762, now 1.1921952756788312

## H-rockage-01 confirm

- tests.age.checks.shift_test.rate_ratio: committed 0.9934692635334919, now 0.9934371292354938
- tests.age.p_bh: committed 0.8676065423651154, now 0.8669859487714117
- tests.age.power: committed 0.9628240828982291, now 0.9628014273393639
- tests.age.tiers.all.terms[0].ci_high: committed 1.0782668570862177, now 1.0782479447274462
- tests.age.tiers.all.terms[0].ci_low: committed 0.9256689902336817, now 0.9256226934118109
- tests.age.tiers.all.terms[0].p_value: committed 0.9806983846440466, now 0.9800105193725405
- tests.age.tiers.all.terms[0].rate_ratio: committed 0.9990586533339495, now 0.9990249079799604
- tests.age.tiers.filtered.terms[0].ci_high: committed 1.0730280677282855, now 1.0730102452387873
- tests.age.tiers.filtered.terms[0].ci_low: committed 0.9198092829718076, now 0.9197650573448448
- tests.age.tiers.filtered.terms[0].p_value: committed 0.8676065423651154, now 0.8669859487714117
- tests.age.tiers.filtered.terms[0].rate_ratio: committed 0.9934692635334919, now 0.9934371292354938
- tests.age.tiers.high_quality.terms[0].ci_high: committed 1.0807349265628767, now 1.0807130999160843
- tests.age.tiers.high_quality.terms[0].ci_low: committed 0.9166228917108163, now 0.9165875836977422
- tests.age.tiers.high_quality.terms[0].p_value: committed 0.9107648185137788, now 0.91022076353994
- tests.age.tiers.high_quality.terms[0].rate_ratio: committed 0.995302151891043, now 0.9952729318747598

## H-rockage-01 explore

- tests.age.checks.shift_test.rate_ratio: committed 1.0414863791454378, now 1.0414731088549343
- tests.age.p_bh: committed 0.21831817772172102, now 0.21849684262465818
- tests.age.power: committed 0.8228847225404421, now 0.8228288551905727
- tests.age.tiers.all.terms[0].ci_low: committed 0.9766261276008886, now 0.9766074172788837
- tests.age.tiers.all.terms[0].p_value: committed 0.19900678332749333, now 0.1991802762892514
- tests.age.tiers.all.terms[0].rate_ratio: committed 1.0459914946044504, now 1.0459769021619885
- tests.age.tiers.filtered.terms[0].ci_low: committed 0.97621689181268, now 0.9761997452569026
- tests.age.tiers.filtered.terms[0].p_value: committed 0.21831817772172102, now 0.21849684262465818
- tests.age.tiers.filtered.terms[0].rate_ratio: committed 1.0414863791454378, now 1.0414731088549343
- tests.age.tiers.high_quality.terms[0].ci_high: committed 1.1139571603241205, now 1.113945725075495
- tests.age.tiers.high_quality.terms[0].ci_low: committed 0.9693642732363686, now 0.9693526342911222
- tests.age.tiers.high_quality.terms[0].p_value: committed 0.27893757522721374, now 0.27908302629570514
- tests.age.tiers.high_quality.terms[0].rate_ratio: committed 1.039148821456311, now 1.0391372493849236

## H-rockage-01 holdout

- tests.age.checks.shift_test.rate_ratio: committed 1.0567443055475012, now 1.056721379261022
- tests.age.p_bh: committed 0.2698293738029489, now 0.2700396491962834
- tests.age.power: committed 0.23108966049075658, now 0.2310622123604011
- tests.age.tiers.all.terms[0].ci_high: committed 1.1648311327651213, now 1.1648112507502069
- tests.age.tiers.all.terms[0].ci_low: committed 0.9521945469759693, now 0.9521689869851503
- tests.age.tiers.all.terms[0].p_value: committed 0.31379144801853553, now 0.31402009344068205
- tests.age.tiers.all.terms[0].rate_ratio: committed 1.0531599369358815, now 1.0531368138355672
- tests.age.tiers.filtered.terms[0].ci_high: committed 1.165588934927144, now 1.1655688861491498
- tests.age.tiers.filtered.terms[0].ci_low: committed 0.9580637683188639, now 0.9580386767843299
- tests.age.tiers.filtered.terms[0].p_value: committed 0.2698293738029489, now 0.2700396491962834
- tests.age.tiers.filtered.terms[0].rate_ratio: committed 1.0567443055475012, now 1.056721379261022
- tests.age.tiers.high_quality.terms[0].ci_low: committed 1.0145525335911298, now 1.0145160221578027
- tests.age.tiers.high_quality.terms[0].p_value: committed 0.030969477135594038, now 0.03100920446329732
- tests.age.tiers.high_quality.terms[0].rate_ratio: committed 1.1709599192218842, now 1.1709332355695936

## H-volcano-01 confirm

- tests.proximity.checks.shift_test.null_median_rate_ratio: committed 1.0423183083359198, now 1.042389120114137
- tests.proximity.checks.shift_test.rate_ratio: committed 1.0721130468077398, now 1.0721545980824239
- tests.proximity.p_bh: committed 0.5338676480587994, now 0.533661444456186
- tests.proximity.tiers.all.terms[0].ci_high: committed 1.3217137123623097, now 1.321780200175043
- tests.proximity.tiers.all.terms[0].ci_low: committed 0.8592577852998345, now 0.859279544434884
- tests.proximity.tiers.all.terms[0].p_value: committed 0.5624872216108925, now 0.5622776816348545
- tests.proximity.tiers.all.terms[0].rate_ratio: committed 1.0656888839078977, now 1.065729181475979
- tests.proximity.tiers.filtered.terms[0].ci_high: committed 1.3350987942014036, now 1.335165883831923
- tests.proximity.tiers.filtered.terms[0].ci_low: committed 0.8609298354006157, now 0.8609533063338746
- tests.proximity.tiers.filtered.terms[0].p_value: committed 0.5338676480587994, now 0.533661444456186
- tests.proximity.tiers.filtered.terms[0].rate_ratio: committed 1.0721130468077398, now 1.0721545980824239
- tests.proximity.tiers.high_quality.terms[0].ci_high: committed 1.3559947803524697, now 1.356042756822302
- tests.proximity.tiers.high_quality.terms[0].ci_low: committed 0.8834314879724375, now 0.8834594424637627
- tests.proximity.tiers.high_quality.terms[0].p_value: committed 0.40875715913899713, now 0.4085873689149083
- tests.proximity.tiers.high_quality.terms[0].rate_ratio: committed 1.094499194375967, now 1.0945358732811157

## H-volcano-01 explore

- tests.proximity.p_bh: committed 0.3542418383775666, now 0.3542514143669844
- tests.proximity.power: committed 0.9999999999999982, now 0.30747836109889054
- tests.proximity.tiers.all.terms[0].p_value: committed 0.265868761305291, now 0.26587761368735363
- tests.proximity.tiers.filtered.terms[0].p_value: committed 0.3542418383775666, now 0.3542514143669844
- tests.proximity.tiers.high_quality.terms[0].p_value: committed 0.8708087385688812, now 0.8708258720750777
