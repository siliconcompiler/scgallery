import argparse
from siliconcompiler import Chip, SiliconCompilerError
import os
import sys
import json
import math
from enum import Enum, auto
from datetime import datetime
from scgallery.checklists import asicflow_rules


class UpdateMethod(Enum):
    All = auto()
    OnlyFailing = auto()
    TightenPassing = auto()


def new_value(chip, metric, job, step, index, operator, padding, margin, bounds):
    value = chip.get('metric', metric, job=job, step=step, index=index)

    if value is None:
        return None

    if operator == '==':
        return value

    sc_type = chip.get('metric', metric, field='type', job=job)

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


def update_rule_value(chip, metric,
                      job, step, index,
                      operator, check_value,
                      padding, margin, bounds,
                      method):
    value = chip.get('metric', metric, job=job, step=step, index=index)

    is_passing = chip._safecompare(value, operator, check_value)
    if method == UpdateMethod.OnlyFailing and is_passing:
        # already passing
        return check_value

    new_check_value = new_value(chip, metric, job, step, index, operator, padding, margin, bounds)

    if new_check_value == check_value:
        # nothing to change
        return check_value

    if method == UpdateMethod.TightenPassing and \
       not chip._safecompare(new_check_value, operator, check_value):
        return check_value

    return new_check_value


def create_rules(chip):
    template = os.path.join(os.path.dirname(__file__), 'checklists', 'asicflow_template.json')
    with open(template) as f:
        new_rules = json.load(f)

    job = chip.get('option', 'jobname')

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
                        chip,
                        criteria['metric'],
                        job, step, index,
                        criteria['operator'],
                        criteria['update']['padding'],
                        criteria['update']['margin'],
                        criteria['update']['bounds'])
                except SiliconCompilerError:
                    continue

                criteria['value'] = value
                used_nodes.add((step, index))

        info['nodes'] = [{"step": step, "index": index} for step, index in used_nodes]

    for rule in list(new_rules.keys()):
        if not new_rules[rule]['nodes']:
            del new_rules[rule]

    return new_rules


def update_rules(chip, method, rules):
    rules["date"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    mainlib = chip.get('asic', 'logiclib')[0]

    if mainlib not in rules:
        raise ValueError(f'{mainlib} is missing from rules')

    job = chip.get('option', 'jobname')

    flow = chip.get('option', 'flow')
    if flow not in rules[mainlib]:
        raise ValueError(f'{flow} is missing from rules')

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
                        chip,
                        criteria['metric'],
                        job, step, index,
                        criteria['operator'],
                        criteria['value'],
                        criteria['update']['padding'],
                        criteria['update']['margin'],
                        criteria['update']['bounds'],
                        method)
                except SiliconCompilerError:
                    continue

                if criteria['value'] != value:
                    criteria_prefix = f"{criteria['metric']}{criteria['operator']}"
                    chip.logger.info(
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

    chip = Chip('check')
    chip.read_manifest(args.cfg)

    mainlib = chip.get('asic', 'logiclib', step='global', index='global')[0]

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
            chip.get('option', 'flow'): {
                "date": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                "rules": create_rules(chip)
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
            chip.summary(generate_image=False, generate_html=False)
            chip.use(asicflow_rules, rules_file=args.rules)
            if not chip.check_checklist('asicflow_rules', verbose=True, require_reports=False):
                sys.exit(1)
            else:
                sys.exit(0)

        if args.update_all:
            update_rules(chip, UpdateMethod.All, rules)
        elif args.tighten_passing:
            update_rules(chip, UpdateMethod.TightenPassing, rules)
        elif args.update_failing:
            update_rules(chip, UpdateMethod.OnlyFailing, rules)

    with open(args.rules, 'w') as f:
        json.dump(rules, f, indent=4, sort_keys=True)
