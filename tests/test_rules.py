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
    chip.set('metric', 'errors', 0, step='writ_gds', index='0')

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
    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '2', '>=', 0.2, 0, {'max': 160}) == 120
    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '2', '<=', 0.2, 0, {'max': 160}) == 160
    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '2', '==', 0.2, 0, {'max': 160}) == 150

    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '2', '>=', 0.2, 0, {'min': 140}) == 140
    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '2', '<=', 0.2, 0, {'min': 140}) == 180
    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '2', '==', 0.2, 0, {'min': 140}) == 150

    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '2', '>=', 0.2, 0, {'min': 140, 'max': 160}) == 140
    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '2', '<=', 0.2, 0, {'min': 140, 'max': 160}) == 160
    assert rules.new_value(metrics_chip, 'cells', 'job0', 'syn', '2', '==', 0.2, 0, {'min': 140, 'max': 160}) == 150


def test_update_value_failing_only(metrics_chip):
    method = rules.UpdateMethod.OnlyFailing
    assert rules.update_rule_value(metrics_chip, 'cells', 'job0', 'syn', '2', '>=', 50, 0.1, 0, {}, method) == 50
    assert rules.update_rule_value(metrics_chip, 'cells', 'job0', 'syn', '2', '>=', 120, 0.1, 0, {}, method) == 120
    assert rules.update_rule_value(metrics_chip, 'cells', 'job0', 'syn', '2', '>=', 200, 0.1, 0, {}, method) == 135


def test_update_value_tightenpassing(metrics_chip):
    method = rules.UpdateMethod.TightenPassing
    assert rules.update_rule_value(metrics_chip, 'cells', 'job0', 'syn', '2', '>=', 50, 0.1, 0, {}, method) == 135
    assert rules.update_rule_value(metrics_chip, 'cells', 'job0', 'syn', '2', '>=', 120, 0.1, 0, {}, method) == 135

    # already thight
    assert rules.update_rule_value(metrics_chip, 'cells', 'job0', 'syn', '2', '>=', 140, 0.1, 0, {}, method) == 140

    # failing this criteria
    assert rules.update_rule_value(metrics_chip, 'cells', 'job0', 'syn', '2', '>=', 200, 0.1, 0, {}, method) == 200


def test_update_value_all(metrics_chip):
    method = rules.UpdateMethod.All
    assert rules.update_rule_value(metrics_chip, 'cells', 'job0', 'syn', '2', '>=', 50, 0.1, 0, {}, method) == 135
    assert rules.update_rule_value(metrics_chip, 'cells', 'job0', 'syn', '2', '>=', 120, 0.1, 0, {}, method) == 135
    assert rules.update_rule_value(metrics_chip, 'cells', 'job0', 'syn', '2', '>=', 140, 0.1, 0, {}, method) == 135
    assert rules.update_rule_value(metrics_chip, 'cells', 'job0', 'syn', '2', '>=', 200, 0.1, 0, {}, method) == 135


def test_create_rules(metrics_chip):
    new_rules = rules.create_rules(metrics_chip)

    assert len(new_rules) == 8

    assert "final_timing" in new_rules
    assert new_rules["final_timing"]["criteria"][0]['value'] is not None
    assert new_rules["final_timing"]["criteria"][1]['value'] is not None

    assert "final_irdrop" in new_rules
    assert new_rules["final_irdrop"]["criteria"][0]['value'] is not None

    assert "fmax" in new_rules
    assert new_rules["fmax"]["criteria"][0]['value'] is not None

    assert "final_cellarea" in new_rules
    assert new_rules["final_cellarea"]["criteria"][0]['value'] is not None

    assert "final_utilization" in new_rules
    assert new_rules["final_utilization"]["criteria"][0]['value'] is not None
    assert new_rules["final_utilization"]["criteria"][1]['value'] is not None

    assert "routing_drcs" in new_rules
    assert new_rules["routing_drcs"]["criteria"][0]['value'] is not None

    assert "errors" in new_rules
    assert new_rules["errors"]["criteria"][0]['value'] == 0

    assert "warnings" in new_rules
    assert new_rules["warnings"]["criteria"][0]['value'] == 0
