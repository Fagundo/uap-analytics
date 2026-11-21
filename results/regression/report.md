# Regression check

Each committed result rerun from the current code and data and compared value by value (relative tolerance 1e-6; run metadata ignored).

| Hypothesis | Split | Compared with | Result | Values differing | New fields | Inputs | Raw files changed | Minutes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H-celebrate-01 | confirm | registered result | same | 0 | 12 | recorded | 0 | 0.1 |
| H-celebrate-01 | explore | registered result | same | 0 | 12 | recorded | 0 | 0.1 |
| H-geo-01 | confirm | registered result | CHANGED | 1 | 6 | recorded | 0 | 0.9 |
| H-geo-01 | explore | registered result | same | 0 | 6 | recorded | 0 | 0.3 |
| H-install-01 | confirm | registered result | CHANGED | 16 | 3 | recorded | 0 | 2.8 |
| H-install-01 | explore | registered result | CHANGED | 10 | 3 | recorded | 0 | 2.8 |
| H-launch-01 | confirm | registered result | same | 0 | 3 | recorded | 0 | 0.4 |
| H-launch-01 | explore | registered result | same | 0 | 3 | recorded | 0 | 0.3 |
| H-persist-01 | confirm | registered result | CHANGED | 8 | 3 | recorded | 0 | 2.3 |
| H-persist-01 | explore | registered result | CHANGED | 2 | 3 | recorded | 0 | 1.1 |
| H-rockage-01 | confirm | registered result | same | 0 | 0 | recorded | 0 | 4.9 |
| H-rockage-01 | explore | registered result | same | 0 | 0 | recorded | 0 | 4.9 |
| H-rockage-01 | holdout | registered result | same | 0 | 0 | recorded | 0 | 5.0 |
| H-rockera-01 | explore | registered result | same | 0 | 0 | recorded | 0 | 17.5 |
| H-rocktype-01 | confirm | registered result | same | 0 | 0 | recorded | 0 | 15.4 |
| H-rocktype-01 | explore | registered result | same | 0 | 0 | recorded | 0 | 15.6 |
| H-rocktype-01 | holdout | registered result | same | 0 | 0 | recorded | 0 | 16.0 |
| H-volcano-01 | confirm | registered result | CHANGED | 16 | 3 | recorded | 0 | 2.8 |
| H-volcano-01 | explore | registered result | CHANGED | 12 | 3 | recorded | 0 | 2.7 |

## H-geo-01 confirm

- tests.storm.tiers.all.terms[1].p_value: committed 4.878253435809939e-07, now 4.878239931526553e-07

## H-install-01 confirm

- tests.proximity.checks.shift_test.null_median_rate_ratio: committed 0.99872858283511, now 0.9987319234349723
- tests.proximity.checks.shift_test.rate_ratio: committed 1.0197305483552357, now 1.0197236601612198
- tests.proximity.p_bh: committed 0.3839458194398284, now 0.38410689438659484
- tests.proximity.power: committed 0.6000632335621124, now 0.6000768104362868
- tests.proximity.tiers.all.terms[0].ci_high: committed 1.0650496457949827, now 1.0650421157890504
- tests.proximity.tiers.all.terms[0].ci_low: committed 0.9729195214019167, now 0.9729131253883136
- tests.proximity.tiers.all.terms[0].p_value: committed 0.44100477079611233, now 0.4411775501154169
- tests.proximity.tiers.all.terms[0].rate_ratio: committed 1.0179428233727745, now 1.0179358788953787
- tests.proximity.tiers.filtered.terms[0].ci_high: committed 1.0655833568920374, now 1.0655758287577317
- tests.proximity.tiers.filtered.terms[0].ci_low: committed 0.9758508187306693, now 0.9758445293422768
- tests.proximity.tiers.filtered.terms[0].p_value: committed 0.3839458194398284, now 0.38410689438659484
- tests.proximity.tiers.filtered.terms[0].rate_ratio: committed 1.0197305483552357, now 1.0197236601612198
- tests.proximity.tiers.high_quality.terms[0].ci_high: committed 1.083453330739537, now 1.0834487343964279
- tests.proximity.tiers.high_quality.terms[0].ci_low: committed 0.9717043830786758, now 0.9716974504249135
- tests.proximity.tiers.high_quality.terms[0].p_value: committed 0.35426416921872694, now 0.35438338321166474
- tests.proximity.tiers.high_quality.terms[0].rate_ratio: committed 1.026058648587301, now 1.0260528119347017

## H-install-01 explore

- tests.proximity.checks.shift_test.rate_ratio: committed 1.0062348929135445, now 1.0062338610676937
- tests.proximity.p_bh: committed 0.7332010934171647, now 0.7332393584617548
- tests.proximity.power: committed 0.9999999999999982, now 0.999456703734892
- tests.proximity.tiers.all.terms[0].ci_high: committed 1.041410412484336, now 1.041408632567754
- tests.proximity.tiers.all.terms[0].p_value: committed 0.7575003564446698, now 0.7575443241717326
- tests.proximity.tiers.all.terms[0].rate_ratio: committed 1.0055375013064776, now 1.0055363694977577
- tests.proximity.tiers.filtered.terms[0].ci_high: committed 1.042846630387507, now 1.0428449692689363
- tests.proximity.tiers.filtered.terms[0].p_value: committed 0.7332010934171647, now 0.7332393584617548
- tests.proximity.tiers.filtered.terms[0].rate_ratio: committed 1.0062348929135445, now 1.0062338610676937
- tests.proximity.tiers.high_quality.terms[0].p_value: committed 0.5589545044968873, now 0.558968742012619

## H-persist-01 confirm

- tests.persistence.checks.local.rate_ratio: committed 1.1885296921712045, now 1.1885280944967342
- tests.persistence.checks.reporting_propensity.rate_ratio: committed 1.178491732101133, now 1.1784903881520512
- tests.persistence.tiers.all.terms[0].ci_high: committed 1.2378075733838139, now 1.2378057703662304
- tests.persistence.tiers.all.terms[0].ci_low: committed 1.1539155489847723, now 1.1539140045947438
- tests.persistence.tiers.all.terms[0].rate_ratio: committed 1.1951256861011281, now 1.19512401590537
- tests.persistence.tiers.filtered.terms[0].ci_high: committed 1.23532778970787, now 1.2353260859213373
- tests.persistence.tiers.filtered.terms[0].ci_low: committed 1.1505372767972954, now 1.150535973120448
- tests.persistence.tiers.filtered.terms[0].rate_ratio: committed 1.1921789593523762, now 1.1921774617843521

## H-persist-01 explore

- tests.persistence.tiers.all.terms[0].ci_high: committed 1.1965935675533608, now 1.1965922642345368
- tests.persistence.tiers.high_quality.terms[0].ci_high: committed 1.1805801744196578, now 1.1805813758274035

## H-volcano-01 confirm

- tests.proximity.checks.shift_test.null_median_rate_ratio: committed 1.0423183083359198, now 1.042389120114137
- tests.proximity.checks.shift_test.rate_ratio: committed 1.0721130468077398, now 1.0721545980824239
- tests.proximity.p_bh: committed 0.5338676480587994, now 0.533661444456186
- tests.proximity.power: committed 0.08963865632306806, now 0.08963835914090545
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

- tests.proximity.checks.shift_test.rate_ratio: committed 1.0624760595403646, now 1.0624749699203617
- tests.proximity.p_bh: committed 0.3542418383775666, now 0.3542514143669844
- tests.proximity.power: committed 0.9999999999999982, now 0.30747836109889054
- tests.proximity.tiers.all.terms[0].ci_low: committed 0.9472047718848812, now 0.947203365659186
- tests.proximity.tiers.all.terms[0].p_value: committed 0.265868761305291, now 0.26587761368735363
- tests.proximity.tiers.all.terms[0].rate_ratio: committed 1.0738193318931757, now 1.0738181494138157
- tests.proximity.tiers.filtered.terms[0].ci_low: committed 0.9346217335784218, now 0.9346204185730544
- tests.proximity.tiers.filtered.terms[0].p_value: committed 0.3542418383775666, now 0.3542514143669844
- tests.proximity.tiers.filtered.terms[0].rate_ratio: committed 1.0624760595403646, now 1.0624749699203617
- tests.proximity.tiers.high_quality.terms[0].ci_high: committed 1.1152030529929169, now 1.115200678029249
- tests.proximity.tiers.high_quality.terms[0].p_value: committed 0.8708087385688812, now 0.8708258720750777
- tests.proximity.tiers.high_quality.terms[0].rate_ratio: committed 1.0083892708306064, now 1.0083880655134239
