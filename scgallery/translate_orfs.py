import json
import argparse
import copy
import os
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser('translate_orfs')

    parser.add_argument('-orfs')
    parser.add_argument('-library')
    parser.add_argument('-rules')

    args = parser.parse_args()

    if not os.path.exists(args.orfs):
        print(f'Unable to open {args.orfs}')
        sys.exit(0)

    with open(args.orfs, 'r') as f:
        orfs_rules = json.load(f)

    rule_mapping = {
        "synth__design__instance__area__stdcell": {
            "key": ["metric", "cellarea"],
            "step": "syn",
            "index": "0"
        },
        "constraints__clocks__count": {
            "key": "sc__metric__timing__clocks",
            "file": "reports/metrics.json",
            "step": "floorplan",
            "index": "0"
        },
        "placeopt__design__instance__area": {
            "key": ["metric", "cellarea"],
            "step": "place",
            "index": "0"
        },
        "placeopt__design__instance__count__stdcell": {
            "key": ["metric", "cells"],
            "step": "place",
            "index": "0"
        },
        "detailedplace__design__violations": {
            "key": "sc__step__design__violations",
            "file": "reports/metrics.json",
            "step": "place",
            "index": "0"
        },
        "cts__timing__setup__ws": {
            "key": ["metric", "setupslack"],
            "step": "cts",
            "index": "0"
        },
        "cts__timing__setup__ws__pre_repair": None,
        "cts__timing__setup__ws__post_repair": None,
        "cts__design__instance__count__setup_buffer": {
            "key": "sc__step__design__instance__count__setup_buffer",
            "file": "reports/metrics.json",
            "step": "cts",
            "index": "0"
        },
        "cts__design__instance__count__hold_buffer": {
            "key": "sc__step__design__instance__count__hold_buffer",
            "file": "reports/metrics.json",
            "step": "cts",
            "index": "0"
        },
        "globalroute__timing__clock__slack": None,
        "globalroute__timing__setup__ws": None,
        "detailedroute__route__wirelength": {
            "key": ["metric", "wirelength"],
            "step": "cts",
            "index": "0"
        },
        "detailedroute__route__drc_errors": {
            "key": "sc__step__route__drc_errors",
            "file": "reports/metrics.json",
            "step": "route",
            "index": "0"
        },
        "finish__timing__setup__ws": {
            "key": ["metric", "setupslack"],
            "step": "export",
            "index": "1"
        },
        "finish__design__instance__area": {
            "key": ["metric", "cellarea"],
            "step": "export",
            "index": "1"
        },
        "finish__timing__drv__max_slew_limit": {
            "key": "sc__metric__timing__drv__max_slew_limit",
            "file": "reports/metrics.json",
            "step": "export",
            "index": "1"
        },
        "finish__timing__drv__max_fanout_limit": {
            "key": "sc__metric__timing__drv__max_fanout_limit",
            "file": "reports/metrics.json",
            "step": "export",
            "index": "1"
        },
        "finish__timing__drv__max_cap_limit": {
            "key": "sc__metric__timing__drv__max_cap_limit",
            "file": "reports/metrics.json",
            "step": "export",
            "index": "1"
        },
        "finish__timing__drv__setup_violation_count": {
            "key": ["metric", "setuppaths"],
            "step": "export",
            "index": "1"
        },
        "finish__timing__drv__hold_violation_count": {
            "key": ["metric", "holdpaths"],
            "step": "export",
            "index": "1"
        },
        "finish__timing__wns_percent_delay": None
    }

    new_rules = []

    for orfs_rule_name, orfs_rule_params in orfs_rules.items():
        if orfs_rule_name not in rule_mapping:
            raise ValueError(orfs_rule_name)

        new_rule = rule_mapping[orfs_rule_name]
        if not new_rule:
            continue

        new_rule = copy.deepcopy(new_rule)
        new_rule['op'] = orfs_rule_params['compare']
        new_rule['value'] = orfs_rule_params['value']

        new_rules.append(new_rule)

    sc_rules = {}
    if os.path.exists(args.rules):
        with open(args.rules, 'r') as f:
            sc_rules = json.load(f)

    sc_rules[args.library] = new_rules
    with open(args.rules, 'w') as f:
        json.dump(sc_rules, f, indent=4)
