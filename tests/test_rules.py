from siliconcompiler import Chip
from siliconcompiler.targets import freepdk45_demo
import pytest
from scgallery import rules


@pytest.fixture
def metrics_chip():
    chip = Chip('test')
    chip.load_target(freepdk45_demo)

    chip.set('metric', 'cells', 4, step='syn', index='0')
    chip.set('metric', 'cells', 75, step='syn', index='1')
    chip.set('metric', 'cells', 150, step='syn', index='2')

    chip.set('metric', 'setupslack', -0.1, step='syn', index='0')
    chip.set('metric', 'setupslack', -2, step='syn', index='1')
    chip.set('metric', 'setupslack', 2, step='syn', index='2')

    chip.set('metric', 'setupslack', -0.5, step='write_data', index='0')
    chip.set('metric', 'holdslack', -0.75, step='write_data', index='0')
    chip.set('metric', 'utilization', 45, step='write_data', index='0')
    chip.set('metric', 'irdrop', 10, step='write_data', index='0')
    chip.set('metric', 'fmax', 1e8, step='write_data', index='0')
    chip.set('metric', 'cellarea', 5e3, step='write_data', index='0')
    chip.set('metric', 'drvs', 5, step='route', index='0')
    chip.set('metric', 'warnings', 0, step='write_data', index='0')
    chip.set('metric', 'errors', 0, step='write_gds', index='0')

    chip.set('metric', 'cells', 5, step='write_data', index='0')
    chip.set('metric', 'totalarea', 5, step='write_data', index='0')
    chip.set('metric', 'peakpower', 5, step='write_data', index='0')
    chip.set('metric', 'leakagepower', 5, step='write_data', index='0')
    chip.set('metric', 'setuppaths', 5, step='write_data', index='0')
    chip.set('metric', 'setuptns', 5, step='write_data', index='0')
    chip.set('metric', 'holdtns', 5, step='write_data', index='0')
    chip.set('metric', 'holdpaths', 5, step='write_data', index='0')
    chip.set('metric', 'logicdepth', 5, step='write_data', index='0')

    for step in chip.getkeys('flowgraph', 'asicflow'):
        for index in chip.getkeys('flowgraph', 'asicflow', step):
            chip.set('metric', 'exetime', 20, step=step, index=index)

    chip.schema.record_history()

    return chip


def __compare_floats(value, expected_value):
    assert f'{value:.5g}' == f'{expected_value:.5g}'


def test_newvalue_padding(metrics_chip):
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '0', '>=', 0.1, 0, {}),
        -0.11
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '0', '>=', 0.2, 0, {}),
        -0.12
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '0', '<=', 0.1, 0, {}),
        -0.09
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '0', '<=', 0.2, 0, {}),
        -0.08
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '0', '==', 0.2, 0, {}),
        -0.1
    )

    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '1', '>=', 0.1, 0, {}),
        -2.20
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '1', '>=', 0.2, 0, {}),
        -2.40
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '1', '<=', 0.1, 0, {}),
        -1.80
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '1', '<=', 0.2, 0, {}),
        -1.60
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '1', '==', 0.2, 0, {}),
        -2.00
    )

    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '2', '>=', 0.1, 0, {}),
        1.80
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '2', '>=', 0.2, 0, {}),
        1.60
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '2', '<=', 0.1, 0, {}),
        2.20
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '2', '<=', 0.2, 0, {}),
        2.40
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '2', '==', 0.2, 0, {}),
        2.00
    )

    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '0', '>=', 0.1, 0, {}) == 3
    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '0', '<=', 0.1, 0, {}) == 5
    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '0', '==', 0.1, 0, {}) == 4

    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '0', '>=', 0.2, 0, {}) == 3
    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '0', '<=', 0.2, 0, {}) == 5
    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '0', '==', 0.2, 0, {}) == 4

    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '1', '>=', 0.1, 0, {}) == 67
    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '1', '<=', 0.1, 0, {}) == 83
    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '1', '==', 0.1, 0, {}) == 75

    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '1', '>=', 0.2, 0, {}) == 60
    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '1', '<=', 0.2, 0, {}) == 90
    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '1', '==', 0.2, 0, {}) == 75

    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '2', '>=', 0.1, 0, {}) == 135
    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '2', '<=', 0.1, 0, {}) == 165
    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '2', '==', 0.1, 0, {}) == 150

    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '2', '>=', 0.2, 0, {}) == 120
    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '2', '<=', 0.2, 0, {}) == 180
    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '2', '==', 0.2, 0, {}) == 150


def test_newvalue_margin(metrics_chip):
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '0', '>=', 0, 0.1, {}),
        -0.20
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '0', '>=', 0, 0.2, {}),
        -0.30
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '0', '<=', 0, 0.1, {}),
        0.0
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '0', '<=', 0, 0.2, {}),
        0.10
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '0', '==', 0, 0.2, {}),
        -0.1
    )

    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '1', '>=', 0, 0.1, {}),
        -2.10
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '1', '>=', 0, 0.2, {}),
        -2.20
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '1', '<=', 0, 0.1, {}),
        -1.90
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '1', '<=', 0, 0.2, {}),
        -1.80
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '1', '==', 0, 0.2, {}),
        -2.00
    )

    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '2', '>=', 0, 0.1, {}),
        1.90
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '2', '>=', 0, 0.2, {}),
        1.80
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '2', '<=', 0, 0.1, {}),
        2.10
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '2', '<=', 0, 0.2, {}),
        2.20
    )
    __compare_floats(
        rules.new_value(metrics_chip, 'setupslack', 'job0', 'syn', '2', '==', 0, 0.2, {}),
        2.00
    )


def test_newvalue_bounds(metrics_chip):
    assert rules.new_value(metrics_chip, 'cells',
                           'job0', 'syn', '2',
                           '>=', 0.2, 0, {'max': 160}) == 120
    assert rules.new_value(metrics_chip, 'cells',
                           'job0', 'syn', '2',
                           '<=', 0.2, 0, {'max': 160}) == 160
    assert rules.new_value(metrics_chip, 'cells',
                           'job0', 'syn', '2',
                           '==', 0.2, 0, {'max': 160}) == 150

    assert rules.new_value(metrics_chip, 'cells',
                           'job0', 'syn', '2',
                           '>=', 0.2, 0, {'min': 140}) == 140
    assert rules.new_value(metrics_chip, 'cells',
                           'job0', 'syn', '2',
                           '<=', 0.2, 0, {'min': 140}) == 180
    assert rules.new_value(metrics_chip, 'cells',
                           'job0', 'syn', '2',
                           '==', 0.2, 0, {'min': 140}) == 150

    assert rules.new_value(metrics_chip, 'cells',
                           'job0', 'syn', '2',
                           '>=', 0.2, 0, {'min': 140, 'max': 160}) == 140
    assert rules.new_value(metrics_chip, 'cells',
                           'job0', 'syn', '2',
                           '<=', 0.2, 0, {'min': 140, 'max': 160}) == 160
    assert rules.new_value(metrics_chip, 'cells',
                           'job0', 'syn', '2',
                           '==', 0.2, 0, {'min': 140, 'max': 160}) == 150


def test_update_value_failing_only(metrics_chip):
    method = rules.UpdateMethod.OnlyFailing
    assert rules.update_rule_value(metrics_chip, 'cells',
                                   'job0', 'syn', '2',
                                   '>=', 50, 0.1, 0, {}, method) == 50
    assert rules.update_rule_value(metrics_chip, 'cells',
                                   'job0', 'syn', '2',
                                   '>=', 120, 0.1, 0, {}, method) == 120
    assert rules.update_rule_value(metrics_chip, 'cells',
                                   'job0', 'syn', '2',
                                   '>=', 200, 0.1, 0, {}, method) == 135


def test_update_value_tightenpassing(metrics_chip):
    method = rules.UpdateMethod.TightenPassing
    assert rules.update_rule_value(metrics_chip, 'cells',
                                   'job0', 'syn', '2',
                                   '>=', 50, 0.1, 0, {}, method) == 135
    assert rules.update_rule_value(metrics_chip, 'cells',
                                   'job0', 'syn', '2',
                                   '>=', 120, 0.1, 0, {}, method) == 135

    # already tight
    assert rules.update_rule_value(metrics_chip, 'cells',
                                   'job0', 'syn', '2',
                                   '>=', 140, 0.1, 0, {}, method) == 140

    # failing this criteria
    assert rules.update_rule_value(metrics_chip, 'cells',
                                   'job0', 'syn', '2',
                                   '>=', 200, 0.1, 0, {}, method) == 200


def test_update_value_all(metrics_chip):
    method = rules.UpdateMethod.All
    assert rules.update_rule_value(metrics_chip, 'cells',
                                   'job0', 'syn', '2',
                                   '>=', 50, 0.1, 0, {}, method) == 135
    assert rules.update_rule_value(metrics_chip, 'cells',
                                   'job0', 'syn', '2',
                                   '>=', 120, 0.1, 0, {}, method) == 135
    assert rules.update_rule_value(metrics_chip, 'cells',
                                   'job0', 'syn', '2',
                                   '>=', 140, 0.1, 0, {}, method) == 135
    assert rules.update_rule_value(metrics_chip, 'cells',
                                   'job0', 'syn', '2',
                                   '>=', 200, 0.1, 0, {}, method) == 135


def test_create_rules(metrics_chip):
    new_rules = rules.create_rules(metrics_chip)

    assert len(new_rules) == 15

    assert "final_timing" in new_rules
    assert len(new_rules["final_timing"]["criteria"]) == 7
    for n in range(len(new_rules["final_timing"]["criteria"])):
        assert new_rules["final_timing"]["criteria"][n]['value'] is not None

    assert "final_power" in new_rules
    for n in range(len(new_rules["final_power"]["criteria"])):
        assert new_rules["final_power"]["criteria"][n]['value'] is not None

    assert "final_fmax" in new_rules
    for n in range(len(new_rules["final_fmax"]["criteria"])):
        assert new_rules["final_fmax"]["criteria"][n]['value'] is not None

    assert "final_area" in new_rules
    for n in range(len(new_rules["final_area"]["criteria"])):
        assert new_rules["final_area"]["criteria"][n]['value'] is not None

    assert "final_utilization" in new_rules
    for n in range(len(new_rules["final_utilization"]["criteria"])):
        assert new_rules["final_utilization"]["criteria"][n]['value'] is not None

    assert "routing_drcs" in new_rules
    for n in range(len(new_rules["routing_drcs"]["criteria"])):
        assert new_rules["routing_drcs"]["criteria"][n]['value'] is not None

    assert "errors" in new_rules
    for n in range(len(new_rules["errors"]["criteria"])):
        assert new_rules["errors"]["criteria"][n]['value'] is not None
