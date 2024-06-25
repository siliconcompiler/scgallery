import pytest
import os
import json
import scgallery
from scgallery.checklists import asicflow_rules
from siliconcompiler import Chip


@pytest.fixture
def mainlib_name():
    return 'testlib'


@pytest.fixture
def flow_name():
    return 'testflow'


@pytest.fixture
def job_name():
    return 'jobtest'


@pytest.fixture
def rules_file(flow_name, mainlib_name):
    root = os.path.dirname(scgallery.__file__)
    with open(os.path.join(root, 'checklists/asicflow_template.json')) as f:
        rules = json.load(f)

    return {
        mainlib_name: {
            flow_name: {
                "rules": rules
            }
        }
    }


@pytest.fixture
def check_chip(mainlib_name, flow_name, job_name):
    chip = Chip('test')

    chip.set('option', 'flow', flow_name)
    chip.set('option', 'jobname', job_name)
    chip.set('asic', 'logiclib', mainlib_name)

    return chip


def test_checklist(rules_file, check_chip):
    with open('testrules.json', 'w') as f:
        json.dump(rules_file, f)

    checklist = asicflow_rules.setup(check_chip, rules_files=['testrules.json'])

    assert len(checklist.getkeys('checklist', 'asicflow_rules')) == 15


def test_checklist_skiprules_all(rules_file, check_chip):
    with open('testrules.json', 'w') as f:
        json.dump(rules_file, f)

    checklist = asicflow_rules.setup(check_chip,
                                     rules_files=['testrules.json'],
                                     skip_rules=['*'])

    assert len(checklist.getkeys('checklist', 'asicflow_rules')) == 0


def test_checklist_skiprules_runtime(rules_file, check_chip):
    with open('testrules.json', 'w') as f:
        json.dump(rules_file, f)

    checklist = asicflow_rules.setup(check_chip,
                                     rules_files=['testrules.json'],
                                     skip_rules=['runtime*'])

    assert len(checklist.getkeys('checklist', 'asicflow_rules')) == 7
