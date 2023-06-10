import argparse
import siliconcompiler
import os
import sys
import json
import math
from enum import Enum, auto


class UpdateMethod(Enum):
    All = auto()
    OnlyFailing = auto()
    TightenPassing = auto()


def __rule_name(rule):
    if isinstance(rule['key'], (list, tuple)):
        base = ",".join(rule['key'][1:])
    else:
        base = rule['key']
    return f"{base}-{rule['step']}{rule['index']}"


def __new_value(value, update_rule):
    if value is None:
        return None

    vtype = type(value)

    new_value = value
    if update_rule['method'] == 'padding':
        new_value *= update_rule['value']
    elif update_rule['method'] == 'sum':
        new_value += update_rule['value']

    if update_rule['bounds']['min_value'] is not None:
        check_value = new_value
        min_value = update_rule['bounds']['min_value']

        if update_rule['bounds']['mode'] == 'sum':
            check_value += min_value
        elif update_rule['bounds']['mode'] == 'multiply':
            check_value = value * min_value
            min_value = new_value

        new_value = min(check_value, min_value)

    if update_rule['bounds']['max_value'] is not None:
        check_value = new_value
        max_value = update_rule['bounds']['max_value']

        if update_rule['bounds']['mode'] == 'sum':
            check_value += max_value
        elif update_rule['bounds']['mode'] == 'multiply':
            check_value = value * max_value
            max_value = new_value

        new_value = max(check_value, max_value)

    if math.isinf(new_value) or math.isnan(new_value):
        new_value = value

    if update_rule['round']:
        new_value = round(new_value)
    else:
        new_value = math.ceil(new_value * 1000) / 1000.0

    return vtype(new_value)


def __get_rule_value(chip, rule, errors=None):
    if errors is None:
        errors = []

    key = rule['key']
    step = rule['step']
    index = rule['index']

    if 'file' in rule:
        metric_file = os.path.join(chip._getworkdir(step=step, index=index),
                                   rule['file'])
        if not os.path.exists(metric_file):
            errors.append(f'Design file {metric_file} does not exist for {key}')
            return None

        with open(metric_file, 'r') as f:
            file_data = json.load(f)

        if key not in file_data:
            errors.append(f'Design file {rule["file"]} does not contain {key}')
            return None

        design_value = file_data[key]
    else:
        if not chip.valid(*key):
            errors.append(f'Design does not contain {key}')
            return None

        design_value = chip.get(*key, step=step, index=index)

    if design_value is None:
        return None

    return design_value


def __check_rule(chip, rule, errors=None):
    if errors is None:
        errors = []

    key = rule['key']
    step = rule['step']
    index = rule['index']
    compare = rule['compare']
    check_value = rule['value']
    design_value = __get_rule_value(chip, rule, errors)

    if design_value is None:
        errors.append(f'{key} in {step}{index} does not contain any data')
        return False

    if not chip._safecompare(design_value, compare, check_value):
        errors.append(f'{key} in {step}{index}: {design_value} {compare} {check_value}')
        return False

    return True


def __check_rules(chip, rules):
    errors = []
    for rule in rules:
        __check_rule(chip, rule, errors=errors)

    return errors


def __update_rule(chip, rule, method):
    is_passing = __check_rule(chip, rule)
    if method == UpdateMethod.OnlyFailing:
        if is_passing:
            return

    metric_value = __get_rule_value(chip, rule)

    old_value = rule['value']
    new_value = __new_value(metric_value, rule['update'])
    op = rule['compare']
    update = new_value != old_value
    if method == UpdateMethod.TightenPassing:
        update = update and chip._safecompare(metric_value, op, new_value)
    if update:
        rule['value'] = new_value
        chip.logger.info(f'Updating rule for {__rule_name(rule)} '
                         f'from {op} {old_value} to {op} {new_value}')


def create_rules(chip):
    # TODO create base list of rules
    new_rules = [
        {
            "key": [
                "metric",
                "cellarea"
            ],
            "step": "syn",
            "index": "0",
            "compare": "<=",
            "value": None,
            "update": {
                "method": "padding",
                "value": 1.15,
                "bounds": {
                    "mode": None,
                    "min_value": None,
                    "max_value": None
                },
                "round": False
            }
        },
        {
            "key": [
                "metric",
                "cellarea"
            ],
            "step": "place",
            "index": "0",
            "compare": "<=",
            "value": None,
            "update": {
                "method": "padding",
                "value": 1.15,
                "bounds": {
                    "mode": None,
                    "min_value": None,
                    "max_value": None
                },
                "round": True
            }
        },
        {
            "key": [
                "metric",
                "cells"
            ],
            "step": "place",
            "index": "0",
            "compare": "<=",
            "value": None,
            "update": {
                "method": "padding",
                "value": 1.15,
                "bounds": {
                    "mode": None,
                    "min_value": None,
                    "max_value": None
                },
                "round": True
            }
        },
        {
            "key": [
                "metric",
                "setupslack"
            ],
            "step": "cts",
            "index": "0",
            "compare": ">=",
            "value": None,
            "update": {
                "method": "padding",
                "value": 0.75,
                "bounds": {
                    "mode": None,
                    "min_value": 0,
                    "max_value": None
                },
                "round": False
            }
        },
        {
            "key": [
                "metric",
                "wirelength"
            ],
            "step": "route",
            "index": "0",
            "compare": "<=",
            "value": None,
            "update": {
                "method": "padding",
                "value": 1.15,
                "bounds": {
                    "mode": None,
                    "min_value": None,
                    "max_value": None
                },
                "round": True
            }
        },
        {
            "key": [
                "metric",
                "setupslack"
            ],
            "step": "export",
            "index": "1",
            "compare": ">=",
            "value": None,
            "update": {
                "method": "padding",
                "value": 0.95,
                "bounds": {
                    "mode": None,
                    "min_value": 0.0,
                    "max_value": None
                },
                "round": False
            }
        },
        {
            "key": [
                "metric",
                "cellarea"
            ],
            "step": "export",
            "index": "1",
            "compare": "<=",
            "value": None,
            "update": {
                "method": "padding",
                "value": 1.15,
                "bounds": {
                    "mode": None,
                    "min_value": None,
                    "max_value": None
                },
                "round": True
            }
        },
        {
            "key": [
                "metric",
                "setuppaths"
            ],
            "step": "export",
            "index": "1",
            "compare": "<=",
            "value": None,
            "update": {
                "method": "padding",
                "value": 1.2,
                "bounds": {
                    "mode": "sum",
                    "min_value": None,
                    "max_value": 10
                },
                "round": True
            }
        },
        {
            "key": [
                "metric",
                "holdpaths"
            ],
            "step": "export",
            "index": "1",
            "compare": "<=",
            "value": None,
            "update": {
                "method": "padding",
                "value": 1.2,
                "bounds": {
                    "mode": "sum",
                    "min_value": None,
                    "max_value": 10
                },
                "round": True
            }
        }
    ]

    design_rules = []
    for new_rule in new_rules:
        metric_value = __get_rule_value(chip, new_rule)
        new_rule['value'] = metric_value
        if new_rule['value'] is not None:
            chip.logger.info(f"Setting {__rule_name(new_rule)} to "
                             f"{new_rule['compare']} {new_rule['value']}")
            design_rules.append(new_rule)
    return design_rules


def update_all_rules(chip, rules):
    for rule in rules:
        __update_rule(chip, rule, UpdateMethod.All)


def update_failing_rules(chip, rules):
    for rule in rules:
        __update_rule(chip, rule, UpdateMethod.OnlyFailing)


def update_passing_rules(chip, rules):
    for rule in rules:
        __update_rule(chip, rule, UpdateMethod.TightenPassing)


def check_rules(chip, rules_files):
    mainlib = chip.get('asic', 'logiclib')[0]

    if not isinstance(rules_files, (list, tuple)):
        rules_files = [rules_files]

    rules = None
    for rules_file in rules_files:
        with open(rules_file, 'r') as f:
            rules = json.load(f)

        if mainlib in rules:
            break

        rules = None

    if not rules:
        return [f'{mainlib} not found in rules']

    return __check_rules(chip, rules[mainlib])


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

    if not os.path.exists(args.rules):
        raise FileNotFoundError(args.rules)

    chip = siliconcompiler.Chip('check')
    chip.read_manifest(args.cfg)

    mainlib = chip.get('asic', 'logiclib')[0]

    with open(args.rules, 'r') as f:
        rules = json.load(f)

    if args.create:
        if mainlib in rules:
            raise ValueError(mainlib)
        rules[mainlib] = create_rules(chip)
    else:
        if mainlib not in rules:
            raise ValueError(mainlib)

        librules = rules[mainlib]
        if args.check:
            errors = check_rules(chip, args.rules)
            for error in errors:
                chip.logger.error(error)
            if errors:
                sys.exit(1)
            else:
                sys.exit(0)

        if args.update_all:
            update_all_rules(chip, librules)
        elif args.tighten_passing:
            update_passing_rules(chip, librules)
        elif args.update_failing:
            update_failing_rules(chip, librules)

    with open(args.rules, 'w') as f:
        json.dump(rules, f, indent=4, sort_keys=True)
