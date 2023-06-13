import argparse
import siliconcompiler
from siliconcompiler import Schema
import os
import sys
import json


def __update_value(operation, value, current_value, margin):
    if operation == ">" or operation == ">=":
        check_value = value / margin
    elif operation == "<" or operation == "<=":
        check_value = value * margin
    elif operation == "==":
        check_value = value
    else:
        check_value = current_value

    return check_value


def __check_rules(chip, rules):
    error = False
    for rule in rules:
        key = rule['key']
        step = rule['step']
        index = rule['index']
        operation = rule['op']
        check_value = rule['value']

        if 'file' in rule:
            with open(os.path.join(chip._getworkdir(step=step, index=index),
                                   rule['file']), 'r') as f:
                file_data = json.load(f)

            if key not in file_data:
                error = True
                chip.logger.error(f'Design file {rule["file"]} does not contain {key}')
                continue

            design_value = file_data[key]
        else:
            if not chip.valid(*key):
                error = True
                chip.logger.error(f'Design design does not contain {key}')
                continue

            design_value = chip.get(*key, step=step, index=index)

        if not chip._safecompare(design_value, operation, check_value):
            error = True
            chip.logger.error(f'{key}: {design_value} {operation} {check_value}')

    return error


def __update_rules(chip, rules, margin):
    margin = 1 + margin
    new_rules = []

    for rule in rules:
        key = rule['key']
        step = rule['step']
        index = rule['index']
        operation = rule['op']

        if 'file' in rule:
            with open(os.path.join(chip._getworkdir(step=step, index=index),
                                   rule['file']), 'r') as f:
                file_data = json.load(f)

            if key not in file_data:
                continue

            file_value = rule['value']
            vtype = type(file_value)
            check_value = __update_value(operation,
                                         file_data[key],
                                         file_value,
                                         margin)
            check_value = vtype(check_value)

            new_rules.append({
                'key': key,
                'file': rule['file'],
                'step': step,
                'index': index,
                'op': operation,
                'value': check_value
            })
        else:
            if not chip.valid(*key):
                continue

            check_value = __update_value(operation,
                                         chip.get(*key, step=step, index=index),
                                         rule['value'],
                                         margin)
            check_value = Schema._check_and_normalize(check_value,
                                                      chip.get(*key, field='type'),
                                                      field='value',
                                                      keypath=key,
                                                      allowed_values=[])

            new_rules.append({
                'key': key,
                'step': step,
                'index': index,
                'op': operation,
                'value': check_value
            })

    return new_rules


if __name__ == "__main__":
    parser = argparse.ArgumentParser('check')
    parser.add_argument('-cfg')
    parser.add_argument('-rules')

    parser.add_argument('-check', action='store_true')
    parser.add_argument('-update', action='store_true')
    parser.add_argument('-margin', default=0.05, type=float)

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

    if mainlib not in rules:
        raise ValueError(mainlib)

    librules = rules[mainlib]
    if args.check:
        if __check_rules(chip, librules):
            sys.exit(0)
        else:
            sys.exit(1)

    if args.update:
        rules[mainlib] = __update_rules(chip, librules, args.margin)
        with open(args.rules, 'w') as f:
            json.dump(rules, f, indent=4)
