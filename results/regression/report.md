# Regression check

Each committed result rerun from the current code and data and compared value by value (relative tolerance 1e-6; run metadata ignored).

| Hypothesis | Split | Result | Values differing | Inputs | Minutes |
| --- | --- | --- | --- | --- | --- |
| H-celebrate-01 | confirm | CHANGED | 12 | missing | 0.2 |
| H-celebrate-01 | explore | CHANGED | 12 | missing | 0.2 |
| H-geo-01 | confirm | CHANGED | 6 | missing | 0.8 |
| H-geo-01 | explore | CHANGED | 6 | missing | 0.3 |
| H-install-01 | confirm | CHANGED | 19 | missing | 4.1 |
| H-install-01 | explore | CHANGED | 13 | missing | 4.0 |
| H-launch-01 | confirm | CHANGED | 3 | missing | 0.4 |
| H-launch-01 | explore | CHANGED | 3 | missing | 0.4 |
| H-persist-01 | confirm | CHANGED | 11 | missing | 1.1 |
| H-persist-01 | explore | CHANGED | 5 | missing | 1.1 |
| H-rockage-01 | confirm | same | 0 | recorded | 4.8 |
| H-rockage-01 | explore | same | 0 | recorded | 4.8 |
| H-rockage-01 | holdout | same | 0 | recorded | 4.9 |
| H-rockera-01 | explore | same | 0 | recorded | 24.7 |
| H-rocktype-01 | confirm | same | 0 | recorded | 12.8 |
| H-rocktype-01 | explore | same | 0 | recorded | 13.0 |
| H-rocktype-01 | holdout | same | 0 | recorded | 13.5 |
| H-volcano-01 | confirm | CHANGED | 19 | missing | 3.5 |
| H-volcano-01 | explore | CHANGED | 15 | missing | 3.5 |

## H-celebrate-01 confirm

- tests.championship.tiers.all.dispersion: committed '<missing>', now 1.0334715069944238
- tests.championship.tiers.filtered.dispersion: committed '<missing>', now 1.037769972832786
- tests.championship.tiers.high_quality.dispersion: committed '<missing>', now 0.9859107416800401
- tests.championship.tiers.unexplained.dispersion: committed '<missing>', now 1.0316004499540314
- tests.july4.tiers.all.dispersion: committed '<missing>', now 1.057999740020395
- tests.july4.tiers.filtered.dispersion: committed '<missing>', now 1.0597448213367753
- tests.july4.tiers.high_quality.dispersion: committed '<missing>', now 1.0779908542976708
- tests.july4.tiers.unexplained.dispersion: committed '<missing>', now 1.0289177013289788
- tests.new_year.tiers.all.dispersion: committed '<missing>', now 1.1894008928617008
- tests.new_year.tiers.filtered.dispersion: committed '<missing>', now 1.195467790287859
- tests.new_year.tiers.high_quality.dispersion: committed '<missing>', now 1.2240740459731523
- tests.new_year.tiers.unexplained.dispersion: committed '<missing>', now 1.054392181153148

## H-celebrate-01 explore

- tests.championship.tiers.all.dispersion: committed '<missing>', now 0.9318571107284832
- tests.championship.tiers.filtered.dispersion: committed '<missing>', now 0.9445150151743832
- tests.championship.tiers.high_quality.dispersion: committed '<missing>', now 0.8559896764654447
- tests.championship.tiers.unexplained.dispersion: committed '<missing>', now 0.9685988964633563
- tests.july4.tiers.all.dispersion: committed '<missing>', now 1.041784297822469
- tests.july4.tiers.filtered.dispersion: committed '<missing>', now 1.0355107993965125
- tests.july4.tiers.high_quality.dispersion: committed '<missing>', now 1.0997048943549372
- tests.july4.tiers.unexplained.dispersion: committed '<missing>', now 0.9971554327818498
- tests.new_year.tiers.all.dispersion: committed '<missing>', now 1.0794667029418081
- tests.new_year.tiers.filtered.dispersion: committed '<missing>', now 1.0476342543741648
- tests.new_year.tiers.high_quality.dispersion: committed '<missing>', now 1.0571485334373032
- tests.new_year.tiers.unexplained.dispersion: committed '<missing>', now 1.0295864263077104

## H-geo-01 confirm

- tests.quake.tiers.all.dispersion: committed '<missing>', now 1.0223844962612245
- tests.quake.tiers.filtered.dispersion: committed '<missing>', now 1.0321359840546056
- tests.quake.tiers.high_quality.dispersion: committed '<missing>', now 1.0320661837931522
- tests.storm.tiers.all.dispersion: committed '<missing>', now 2.692387853273045
- tests.storm.tiers.filtered.dispersion: committed '<missing>', now 2.4567603605564723
- tests.storm.tiers.high_quality.dispersion: committed '<missing>', now 1.9495393970367334

## H-geo-01 explore

- tests.quake.tiers.all.dispersion: committed '<missing>', now 1.0017170149664651
- tests.quake.tiers.filtered.dispersion: committed '<missing>', now 1.0210186098914091
- tests.quake.tiers.high_quality.dispersion: committed '<missing>', now 1.0452870978664157
- tests.storm.tiers.all.dispersion: committed '<missing>', now 2.0285248141455456
- tests.storm.tiers.filtered.dispersion: committed '<missing>', now 1.894753356442485
- tests.storm.tiers.high_quality.dispersion: committed '<missing>', now 1.4647715846118292

## H-install-01 confirm

- tests.proximity.checks.shift_test.null_median_rate_ratio: committed 0.99872858283511, now 0.9987319234316444
- tests.proximity.checks.shift_test.rate_ratio: committed 1.0197305483552357, now 1.0197236601605084
- tests.proximity.p_bh: committed 0.3839458194398284, now 0.38410689440420454
- tests.proximity.power: committed 0.6000632335621124, now 0.6000768104357586
- tests.proximity.tiers.all.dispersion: committed '<missing>', now nan
- tests.proximity.tiers.all.terms[0].ci_high: committed 1.0650496457949827, now 1.0650421157905459
- tests.proximity.tiers.all.terms[0].ci_low: committed 0.9729195214019167, now 0.9729131253899759
- tests.proximity.tiers.all.terms[0].p_value: committed 0.44100477079611233, now 0.4411775500738888
- tests.proximity.tiers.all.terms[0].rate_ratio: committed 1.0179428233727745, now 1.017935878896963
- tests.proximity.tiers.filtered.dispersion: committed '<missing>', now nan
- tests.proximity.tiers.filtered.terms[0].ci_high: committed 1.0655833568920374, now 1.0655758287570494
- tests.proximity.tiers.filtered.terms[0].ci_low: committed 0.9758508187306693, now 0.9758445293415398
- tests.proximity.tiers.filtered.terms[0].p_value: committed 0.3839458194398284, now 0.38410689440420454
- tests.proximity.tiers.filtered.terms[0].rate_ratio: committed 1.0197305483552357, now 1.0197236601605084
- tests.proximity.tiers.high_quality.dispersion: committed '<missing>', now nan
- tests.proximity.tiers.high_quality.terms[0].ci_high: committed 1.083453330739537, now 1.0834487343966466
- tests.proximity.tiers.high_quality.terms[0].ci_low: committed 0.9717043830786758, now 0.9716974504251656
- tests.proximity.tiers.high_quality.terms[0].p_value: committed 0.35426416921872694, now 0.3543833832070943
- tests.proximity.tiers.high_quality.terms[0].rate_ratio: committed 1.026058648587301, now 1.0260528119349384

## H-install-01 explore

- tests.proximity.checks.shift_test.rate_ratio: committed 1.0062348929135445, now 1.006233861067091
- tests.proximity.p_bh: committed 0.7332010934171647, now 0.7332393584866561
- tests.proximity.power: committed 0.9999999999999982, now 0.9994567037348859
- tests.proximity.tiers.all.dispersion: committed '<missing>', now nan
- tests.proximity.tiers.all.terms[0].ci_high: committed 1.041410412484336, now 1.0414086325677037
- tests.proximity.tiers.all.terms[0].p_value: committed 0.7575003564446698, now 0.7575443241735997
- tests.proximity.tiers.all.terms[0].rate_ratio: committed 1.0055375013064776, now 1.0055363694977129
- tests.proximity.tiers.filtered.dispersion: committed '<missing>', now nan
- tests.proximity.tiers.filtered.terms[0].ci_high: committed 1.042846630387507, now 1.0428449692683344
- tests.proximity.tiers.filtered.terms[0].p_value: committed 0.7332010934171647, now 0.7332393584866561
- tests.proximity.tiers.filtered.terms[0].rate_ratio: committed 1.0062348929135445, now 1.006233861067091
- tests.proximity.tiers.high_quality.dispersion: committed '<missing>', now nan
- tests.proximity.tiers.high_quality.terms[0].p_value: committed 0.5589545044968873, now 0.558968742010284

## H-launch-01 confirm

- tests.twilight.tiers.all.dispersion: committed '<missing>', now 1.33077254505626
- tests.twilight.tiers.filtered.dispersion: committed '<missing>', now 1.3253510703500386
- tests.twilight.tiers.high_quality.dispersion: committed '<missing>', now 1.264613397204841

## H-launch-01 explore

- tests.twilight.tiers.all.dispersion: committed '<missing>', now 1.2596880184333354
- tests.twilight.tiers.filtered.dispersion: committed '<missing>', now 1.2549874929928118
- tests.twilight.tiers.high_quality.dispersion: committed '<missing>', now 1.1694438595585321

## H-persist-01 confirm

- tests.persistence.checks.local.rate_ratio: committed 1.1885296921712045, now 1.1885280944967342
- tests.persistence.checks.reporting_propensity.rate_ratio: committed 1.178491732101133, now 1.1784903881520512
- tests.persistence.tiers.all.dispersion: committed '<missing>', now nan
- tests.persistence.tiers.all.terms[0].ci_high: committed 1.2378075733838139, now 1.2378057703662304
- tests.persistence.tiers.all.terms[0].ci_low: committed 1.1539155489847723, now 1.1539140045947438
- tests.persistence.tiers.all.terms[0].rate_ratio: committed 1.1951256861011281, now 1.19512401590537
- tests.persistence.tiers.filtered.dispersion: committed '<missing>', now nan
- tests.persistence.tiers.filtered.terms[0].ci_high: committed 1.23532778970787, now 1.2353260859213373
- tests.persistence.tiers.filtered.terms[0].ci_low: committed 1.1505372767972954, now 1.150535973120448
- tests.persistence.tiers.filtered.terms[0].rate_ratio: committed 1.1921789593523762, now 1.1921774617843521
- tests.persistence.tiers.high_quality.dispersion: committed '<missing>', now nan

## H-persist-01 explore

- tests.persistence.tiers.all.dispersion: committed '<missing>', now nan
- tests.persistence.tiers.all.terms[0].ci_high: committed 1.1965935675533608, now 1.1965922642345368
- tests.persistence.tiers.filtered.dispersion: committed '<missing>', now nan
- tests.persistence.tiers.high_quality.dispersion: committed '<missing>', now nan
- tests.persistence.tiers.high_quality.terms[0].ci_high: committed 1.1805801744196578, now 1.1805813758274035

## H-volcano-01 confirm

- tests.proximity.checks.shift_test.null_median_rate_ratio: committed 1.0423183083359198, now 1.042389120114137
- tests.proximity.checks.shift_test.rate_ratio: committed 1.0721130468077398, now 1.0721545980824239
- tests.proximity.p_bh: committed 0.5338676480587994, now 0.533661444456186
- tests.proximity.power: committed 0.08963865632306806, now 0.08963835914090545
- tests.proximity.tiers.all.dispersion: committed '<missing>', now nan
- tests.proximity.tiers.all.terms[0].ci_high: committed 1.3217137123623097, now 1.321780200175043
- tests.proximity.tiers.all.terms[0].ci_low: committed 0.8592577852998345, now 0.859279544434884
- tests.proximity.tiers.all.terms[0].p_value: committed 0.5624872216108925, now 0.5622776816348545
- tests.proximity.tiers.all.terms[0].rate_ratio: committed 1.0656888839078977, now 1.065729181475979
- tests.proximity.tiers.filtered.dispersion: committed '<missing>', now nan
- tests.proximity.tiers.filtered.terms[0].ci_high: committed 1.3350987942014036, now 1.335165883831923
- tests.proximity.tiers.filtered.terms[0].ci_low: committed 0.8609298354006157, now 0.8609533063338746
- tests.proximity.tiers.filtered.terms[0].p_value: committed 0.5338676480587994, now 0.533661444456186
- tests.proximity.tiers.filtered.terms[0].rate_ratio: committed 1.0721130468077398, now 1.0721545980824239
- tests.proximity.tiers.high_quality.dispersion: committed '<missing>', now nan
- tests.proximity.tiers.high_quality.terms[0].ci_high: committed 1.3559947803524697, now 1.356042756822302
- tests.proximity.tiers.high_quality.terms[0].ci_low: committed 0.8834314879724375, now 0.8834594424637627
- tests.proximity.tiers.high_quality.terms[0].p_value: committed 0.40875715913899713, now 0.4085873689149083
- tests.proximity.tiers.high_quality.terms[0].rate_ratio: committed 1.094499194375967, now 1.0945358732811157

## H-volcano-01 explore

- tests.proximity.checks.shift_test.rate_ratio: committed 1.0624760595403646, now 1.0624749699203617
- tests.proximity.p_bh: committed 0.3542418383775666, now 0.3542514143669844
- tests.proximity.power: committed 0.9999999999999982, now 0.30747836109889054
- tests.proximity.tiers.all.dispersion: committed '<missing>', now nan
- tests.proximity.tiers.all.terms[0].ci_low: committed 0.9472047718848812, now 0.947203365659186
- tests.proximity.tiers.all.terms[0].p_value: committed 0.265868761305291, now 0.26587761368735363
- tests.proximity.tiers.all.terms[0].rate_ratio: committed 1.0738193318931757, now 1.0738181494138157
- tests.proximity.tiers.filtered.dispersion: committed '<missing>', now nan
- tests.proximity.tiers.filtered.terms[0].ci_low: committed 0.9346217335784218, now 0.9346204185730544
- tests.proximity.tiers.filtered.terms[0].p_value: committed 0.3542418383775666, now 0.3542514143669844
- tests.proximity.tiers.filtered.terms[0].rate_ratio: committed 1.0624760595403646, now 1.0624749699203617
- tests.proximity.tiers.high_quality.dispersion: committed '<missing>', now nan
- tests.proximity.tiers.high_quality.terms[0].ci_high: committed 1.1152030529929169, now 1.115200678029249
- tests.proximity.tiers.high_quality.terms[0].p_value: committed 0.8708087385688812, now 0.8708258720750777
- tests.proximity.tiers.high_quality.terms[0].rate_ratio: committed 1.0083892708306064, now 1.0083880655134239
