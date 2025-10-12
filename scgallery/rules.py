import argparse
import sys
import json
import math

import os.path

from typing import Union, Dict, Optional

from enum import Enum, auto
from datetime import datetime
from scgallery.checklists import asicflow_rules
from siliconcompiler import utils, ASIC
from siliconcompiler.flowgraph import RuntimeFlowgraph


class UpdateMethod(Enum):
    All = auto()
    OnlyFailing = auto()
    TightenPassing = auto()


def new_value(project: ASIC,
              metric: str, job: str,
              step: str, index: str,
              operator: str,
              padding: Optional[float],
              margin: Optional[Union[float, int]],
              bounds: Optional[Dict[str, Union[float, int]]]) -> Optional[Union[int, float]]:
    jobproject = project.history(job)
    value: Union[None, float, int] = jobproject.get('metric', metric, step=step, index=index)

    if value is None:
        return None

    if operator == '==':
        return value

    sc_type: str = jobproject.get('metric', metric, field='type')

    newvalue = value
    if padding:
        if '>' in operator:
            if newvalue < 0:
                newvalue *= 1 + padding
            else:
                newvalue *= 1 - padding
        elif '<' in operator:
            if newvalue < 0:
                newvalue *= 1 - padding
            else:
                newvalue *= 1 + padding
    elif margin:
        if '>' in operator:
            newvalue -= margin
        elif '<' in operator:
            newvalue += margin

    if sc_type == 'int':
        if '>' in operator:
            newvalue = math.floor(newvalue)
        elif '<' in operator:
            newvalue = math.ceil(newvalue)
        newvalue = int(newvalue)

    if bounds:
        if 'max' in bounds:
            newvalue = min(bounds['max'], newvalue)
        if 'min' in bounds:
            newvalue = max(bounds['min'], newvalue)

    return newvalue


def update_rule_value(project: ASIC, metric: str,
                      job: str,
                      step: str, index: str,
                      operator: str,
                      check_value: Union[float, int],
                      padding: Optional[float],
                      margin: Optional[Union[float, int]],
                      bounds: Optional[Dict[str, Union[float, int]]],
                      method: UpdateMethod) -> Optional[Union[float, int]]:
    jobproject = project.history(job)
    value: Union[float, int] = jobproject.get('metric', metric, step=step, index=index)

    is_passing = utils.safecompare(value, operator, check_value)
    if method == UpdateMethod.OnlyFailing and is_passing:
        # already passing
        return check_value

    new_check_value = new_value(project,
                                metric,
                                job, step, index,
                                operator,
                                padding,
                                margin,
                                bounds)

    if new_check_value is None:
        return None

    if new_check_value == check_value:
        # nothing to change
        return check_value

    if method == UpdateMethod.TightenPassing and \
       not utils.safecompare(new_check_value, operator, check_value):
        return check_value

    return new_check_value


def create_rules(project: ASIC) -> Dict:
    template = os.path.join(os.path.dirname(__file__), 'checklists', 'asicflow_template.json')
    with open(template) as f:
        new_rules: Dict = json.load(f)

    job = project.option.get_jobname()

    # create initial check values
    for info in new_rules.values():
        nodes = set([(node['step'], node['index']) for node in info['nodes']])

        used_nodes = set()
        for criteria in info['criteria']:
            if len(nodes) > 1:
                used_nodes = nodes
                continue

            for step, index in nodes:
                if step == '*' or index == '*':
                    used_nodes.add((step, index))
                    continue

                try:
                    value = new_value(
                        project,
                        criteria['metric'],
                        job, step, index,
                        criteria['operator'],
                        criteria['update']['padding'],
                        criteria['update']['margin'],
                        criteria['update']['bounds'])
                except ValueError:
                    continue

                criteria['value'] = value
                used_nodes.add((step, index))

        info['nodes'] = [{"step": step, "index": index} for step, index in used_nodes]

    for rule in list(new_rules.keys()):
        if not new_rules[rule]['nodes']:
            del new_rules[rule]

    return new_rules


def update_rules(project: ASIC, method: UpdateMethod, rules: Dict):
    rules["date"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    mainlib = project.get("asic", "mainlib")

    if mainlib not in rules:
        raise ValueError(f'{mainlib} is missing from rules')

    job = project.option.get_jobname()

    flow = project.option.get_flow()
    if flow not in rules[mainlib]:
        raise ValueError(f'{flow} is missing from rules for {mainlib}')

    for rule, info in rules[mainlib][flow]['rules'].items():
        nodes = set([(node['step'], node['index']) for node in info['nodes']])

        if len(nodes) > 1:
            continue

        for criteria in info['criteria']:
            for step, index in nodes:
                if step == '*' or index == '*':
                    continue

                try:
                    value = update_rule_value(
                        project,
                        criteria['metric'],
                        job, step, index,
                        criteria['operator'],
                        criteria['value'],
                        criteria['update']['padding'],
                        criteria['update']['margin'],
                        criteria['update']['bounds'],
                        method)
                except ValueError:
                    continue

                if criteria['value'] != value:
                    criteria_prefix = f"{criteria['metric']}{criteria['operator']}"
                    project.logger.info(
                        f"Updating {rule} for {job}/{step}{index} from "
                        f"{criteria_prefix}{criteria['value']} to {criteria_prefix}{value}")
                    criteria['value'] = value


if __name__ == "__main__":
    parser = argparse.ArgumentParser('check')
    parser.add_argument('-cfg',
                        required=True,
                        metavar='<file>',
                        help='Path the the manifest file')
    parser.add_argument('-rules',
                        required=True,
                        metavar='<file>',
                        help='Path the the rules JSON file')

    mode_parser = parser.add_mutually_exclusive_group(required=True)
    mode_parser.add_argument('-check',
                             action='store_true')
    mode_parser.add_argument('-create',
                             action='store_true')
    mode_parser.add_argument('-update_all',
                             action='store_true')
    mode_parser.add_argument('-tighten_passing',
                             action='store_true')
    mode_parser.add_argument('-update_failing',
                             action='store_true')

    args = parser.parse_args()

    if not os.path.exists(args.cfg):
        raise FileNotFoundError(args.cfg)

    project: ASIC = ASIC.from_manifest(args.cfg)

    mainlib: str = project.get('asic', 'mainlib')

    if args.create:
        # create initial set of rules
        if args.rules and os.path.exists(args.rules):
            with open(args.rules, 'r') as f:
                rules = json.load(f)
        else:
            rules = {}

        if mainlib in rules:
            raise ValueError(mainlib)

        rules[mainlib] = {
            project.option.get_flow(): {
                "date": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                "rules": create_rules(project)
            }
        }
    else:
        if args.rules:
            if not os.path.exists(args.rules):
                raise FileNotFoundError(args.rules)
        else:
            raise ValueError('rules file is required.')

        with open(args.rules, 'r') as f:
            rules = json.load(f)

        if args.check:
            runtime = RuntimeFlowgraph(
                project.get("flowgraph", project.option.get_flow(), field='schema'),
                from_steps=project.option.get_from(),
                to_steps=project.option.get_to(),
                prune_nodes=project.option.get_prune())
            project.summary()
            checklist = asicflow_rules.ASICChecklist(
                job=project.option.get_jobname(),
                flow=project.option.get_flow(),
                mainlib=mainlib,
                flow_nodes=runtime.get_nodes(),
                rules_files=args.rules)
            project.add_dep(checklist)
            if not checklist.check(require_reports=False):
                sys.exit(1)
            else:
                sys.exit(0)

        if args.update_all:
            update_rules(project, UpdateMethod.All, rules)
        elif args.tighten_passing:
            update_rules(project, UpdateMethod.TightenPassing, rules)
        elif args.update_failing:
            update_rules(project, UpdateMethod.OnlyFailing, rules)

    with open(args.rules, 'w') as f:
        json.dump(rules, f, indent=4, sort_keys=True)
