import pytest
import json
import scgallery

import os.path

from scgallery.checklists.asicflow_rules import ASICChecklist
from siliconcompiler import ASIC


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
def check_project(mainlib_name, flow_name, job_name):
    proj = ASIC()
    proj.option.set_flow(flow_name)
    proj.option.set_jobname(job_name)
    proj.set("asic", "asiclib", mainlib_name)

    return proj


def test_checklist(rules_file, check_project, mainlib_name):
    with open('testrules.json', 'w') as f:
        json.dump(rules_file, f)

    checklist = ASICChecklist(
        job=check_project.get('option', 'jobname'),
        flow=check_project.get('option', 'flow'),
        mainlib=mainlib_name,
        flow_nodes=[],
        rules_files=['testrules.json'])

    assert len(checklist.getkeys()) == 15


def test_checklist_skiprules_all(rules_file, check_project, mainlib_name):
    with open('testrules.json', 'w') as f:
        json.dump(rules_file, f)

    checklist = ASICChecklist(
        job=check_project.get('option', 'jobname'),
        flow=check_project.get('option', 'flow'),
        mainlib=mainlib_name,
        flow_nodes=[],
        rules_files=['testrules.json'],
        skip_rules=['*'])

    assert len(checklist.getkeys()) == 0


def test_checklist_skiprules_runtime(rules_file, check_project, mainlib_name):
    with open('testrules.json', 'w') as f:
        json.dump(rules_file, f)

    checklist = ASICChecklist(
        job=check_project.get('option', 'jobname'),
        flow=check_project.get('option', 'flow'),
        mainlib=mainlib_name,
        flow_nodes=[],
        rules_files=['testrules.json'],
        skip_rules=['runtime*'])

    assert len(checklist.getkeys()) == 7
