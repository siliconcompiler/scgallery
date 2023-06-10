#!/usr/bin/env python3

import argparse
import json
import copy
import glob
import os
import shutil
import scgallery
from scgallery.designs import all_designs
import git
import tempfile


def __rule_mapping(rule):
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
            "step": "route",
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

    if rule not in rule_mapping:
        raise ValueError(f'{rule} not found in mapping')

    return rule_mapping[rule]


def __scale_mapping(library, rule):
    scale_adj = {
        "asap7sc7p5t_rvt": {
            "cts__timing__setup__ws": 0.001,
            "cts__timing__setup__ws__pre_repair": 0.001,
            "cts__timing__setup__ws__post_repair": 0.001,
            "globalroute__timing__clock__slack": 0.001,
            "globalroute__timing__setup__ws": 0.001,
            "finish__timing__setup__ws": 0.001,
            "finish__timing__drv__max_slew_limit": 1,
            "finish__timing__drv__max_cap_limit": 1
        }
    }

    if library in scale_adj:
        scale = scale_adj[library]
    else:
        return 1

    if rule in scale:
        return scale[rule]
    else:
        return 1


def __update_rule_mapping(rule):
    rules_dict = {
        # synth
        'synth__design__instance__area__stdcell': {
            'mode': 'padding',
            'padding': 15,
            'round_value': False,
            'compare': '<=',
        },
        # clock
        'constraints__clocks__count': {
            'mode': 'direct',
            'round_value': True,
            'compare': '==',
        },
        # floorplan
        # place
        'placeopt__design__instance__area': {
            'mode': 'padding',
            'padding': 15,
            'round_value': True,
            'compare': '<=',
        },
        'placeopt__design__instance__count__stdcell': {
            'mode': 'padding',
            'padding': 15,
            'round_value': True,
            'compare': '<=',
        },
        'detailedplace__design__violations': {
            'mode': 'direct',
            'round_value': True,
            'compare': '==',
        },
        # cts
        'cts__design__instance__count__setup_buffer': {
            'mode': 'metric',
            'padding': 10,
            'metric': 'placeopt__design__instance__count__stdcell',
            'round_value': True,
            'compare': '<=',
        },
        'cts__design__instance__count__hold_buffer': {
            'mode': 'metric',
            'padding': 10,
            'metric': 'placeopt__design__instance__count__stdcell',
            'round_value': True,
            'compare': '<=',
        },
        # route
        'detailedroute__route__wirelength': {
            'mode': 'padding',
            'padding': 15,
            'round_value': True,
            'compare': '<=',
        },
        'detailedroute__route__drc_errors': {
            'mode': 'direct',
            'round_value': True,
            'compare': '<=',
        },
        # finish
        'finish__timing__setup__ws': {
            'mode': 'period',
            'padding': 5,
            'round_value': False,
            'compare': '>=',
        },
        'finish__design__instance__area': {
            'mode': 'padding',
            'padding': 15,
            'round_value': True,
            'compare': '<=',
        },
        'finish__timing__drv__setup_violation_count': {
            'mode': 'padding',
            'padding': 5,
            'min_max': max,
            'min_max_sum': 20,
            'round_value': True,
            'compare': '<=',
        },
        'finish__timing__drv__hold_violation_count': {
            'mode': 'padding',
            'padding': 25,
            'min_max': max,
            'min_max_sum': 100,
            'round_value': True,
            'compare': '<=',
        },
        'finish__timing__wns_percent_delay': {
            'mode': 'padding',
            'padding': 20,
            'min_max': min,
            'min_max_sum': -10,
            'round_value': False,
            'compare': '>=',
        }
    }

    if rule not in rules_dict:
        raise ValueError(f'{rule} is not accounted for in translation')

    orfs_rule = rules_dict[rule]

    method = None
    value = 0.0
    min_max_mode = None
    min_value = None
    max_value = None

    # Mode
    if orfs_rule['mode'] == 'direct':
        method = 'sum'
        value = 0
    elif orfs_rule['mode'] == 'sum_fixed':
        method = 'sum'
        value = orfs_rule['padding']
    elif orfs_rule['mode'] == 'period':
        method = 'padding'
        value = (100.0 - orfs_rule['padding']) / 100.0
        min_value = 0.0
    elif orfs_rule['mode'] == 'padding':
        method = 'padding'
        value = (100.0 + orfs_rule['padding']) / 100.0
    elif orfs_rule['mode'] == 'metric':
        method = 'padding'
        value = (100.0 + orfs_rule['padding']) / 100.0
    else:
        raise ValueError(f"{orfs_rule['mode']} unknown mode")

    # Bounding
    if 'min_max' in orfs_rule:
        min_max = orfs_rule['min_max']
        if 'min_max_direct' in orfs_rule:
            min_max_mode = None
            if min_max == max:
                max_value = orfs_rule['min_max_direct']
            if min_max == min:
                min_value = orfs_rule['min_max_direct']
        elif 'min_max_sum' in orfs_rule:
            min_max_mode = 'sum'
            if min_max == max:
                max_value = orfs_rule['min_max_sum']
            if min_max == min:
                min_value = orfs_rule['min_max_sum']

    if rule == 'cts__design__instance__count__setup_buffer' or \
       rule == 'cts__design__instance__count__hold_buffer':
        min_max_mode = 'multiply'
        max_value = 1.1

    # Round
    round_value = False
    if 'round_value' in orfs_rule:
        round_value = orfs_rule['round_value']

    update_rule = {
        'method': method,  # padding / sum
        'value': value,  # padding
        'bounds': {
            'mode': min_max_mode,  # sum / None / multiply,
            'min_value': min_value,
            'max_value': max_value
        },
        'round': round_value
    }

    return update_rule


def translate(orfs, library, rules):
    if not os.path.exists(orfs):
        return False

    with open(orfs, 'r') as f:
        orfs_rules = json.load(f)

    new_rules = []

    for orfs_rule_name, orfs_rule_params in orfs_rules.items():
        new_rule = __rule_mapping(orfs_rule_name)
        if not new_rule:
            continue

        new_rule = copy.deepcopy(new_rule)
        new_rule['compare'] = orfs_rule_params['compare']
        new_rule['value'] = orfs_rule_params['value']

        new_rule['value'] *= __scale_mapping(library, orfs_rule_name)

        new_rule['update'] = __update_rule_mapping(orfs_rule_name)

        new_rules.append(new_rule)

    sc_rules = {}
    if os.path.exists(rules):
        with open(rules, 'r') as f:
            sc_rules = json.load(f)

    os.makedirs(os.path.dirname(rules), exist_ok=True)
    sc_rules[library] = new_rules
    with open(rules, 'w') as f:
        json.dump(sc_rules, f, indent=4, sort_keys=True)

    return True


def __map_name(name):
    name_map = {
        "ariane": "ariane133",
        "tiny_rocket": "tinyRocket",
        "sram_bridge": "sram-64x16",
        "mock_alu": "mock-alu"
    }
    if name in name_map:
        return name_map[name]
    return name


def __map_sdc(repo_work_dir, orfs_name, orfs_library):
    sdc_map = {
        ("nangate45", "ariane133"): "ariane.sdc",
        ("asap7", "jpeg"): "jpeg_encoder15_7nm.sdc",
        ("asap7", "mock-alu"): "constraints.sdc",
        ("sky130hd", "mock-alu"): "constraints.sdc",
        ("asap7", "sram-64x16"): "constraints.sdc"
    }

    sdc = 'constraint.sdc'
    if (orfs_library, orfs_name) in sdc_map:
        sdc = sdc_map[(orfs_library, orfs_name)]

    return os.path.join(repo_work_dir,
                        'flow',
                        'designs',
                        orfs_library,
                        orfs_name,
                        sdc)


def __get_orfs_designs(orfs_dir):
    design_map = {}

    for tech_dir in glob.glob(os.path.join(orfs_dir, 'flow', 'designs', '*')):
        tech = os.path.basename(tech_dir)
        if tech in ("src", "harness.mk"):
            continue

        if tech in ("gf55",
                    "gf12",
                    "intel22",
                    "intel16",
                    "tsmc65lp",
                    "sky130hd_fakestack"):
            # Skip tech nodes that will not be supported
            continue

        for design_dir in glob.glob(os.path.join(tech_dir, "*")):
            design = os.path.basename(design_dir)

            if design in ("aes-block",
                          "ariane136",
                          "chameleon_hier",
                          "mock-array-big",
                          "mock-array",
                          "swerv_wrapper",
                          "uart-blocks"):
                continue

            design_map.setdefault(design, set()).add(tech)

    return design_map


def convert_all(local=None, mirror=False):
    if local:
        repo_work_dir = local
    else:
        orfs_path = 'https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts.git'
        repo_dir = tempfile.TemporaryDirectory(prefix='orfs_')
        repo_work_dir = repo_dir.name
        print(f"Cloning into: {orfs_path}")
        git.Repo.clone_from(orfs_path, repo_work_dir)

    orfs_designs = __get_orfs_designs(repo_work_dir)
    designs_found = {}

    for design in all_designs().keys():
        orfs_name = __map_name(design)

        if not orfs_name:
            continue

        for orfs_library, library in [('nangate45', 'nangate45'),
                                      ('sky130hd', 'sky130hd'),
                                      ('sky130hs', 'sky130hs'),
                                      ('asap7', 'asap7sc7p5t_rvt'),
                                      ('gf180', 'gf180mcu_fd_sc_mcu9t5v0')]:

            gallery_rules = os.path.join(os.path.dirname(scgallery.__file__),
                                         'designs',
                                         design,
                                         'rules.json')
            gallery_sdc = os.path.join(os.path.dirname(scgallery.__file__),
                                       'designs',
                                       design,
                                       'constraints',
                                       f'{library}.sdc')

            orfs_rules = os.path.join(repo_work_dir,
                                      'flow',
                                      'designs',
                                      orfs_library,
                                      orfs_name,
                                      'rules-base.json')
            orfs_base = os.path.join(os.path.dirname(__file__),
                                     'designs',
                                     design)
            rules = os.path.join(orfs_base, 'rules.json')
            if translate(orfs=orfs_rules,
                         library=library,
                         rules=rules):
                os.makedirs(orfs_base, exist_ok=True)
                if mirror:
                    os.makedirs(os.path.dirname(gallery_rules), exist_ok=True)
                    shutil.copyfile(rules, gallery_rules)
                orfs_sdc = __map_sdc(repo_work_dir, orfs_name, orfs_library)
                if os.path.exists(orfs_sdc):
                    orfs_gallery_sdc = os.path.join(orfs_base, 'constraints', f'{library}.sdc')
                    sdcs = [orfs_gallery_sdc]
                    if mirror:
                        sdcs.append(gallery_sdc)
                    for sdc in sdcs:
                        os.makedirs(os.path.dirname(sdc), exist_ok=True)
                        shutil.copyfile(orfs_sdc, sdc)
                else:
                    print(f"Unable to find ORFS SDC: {orfs_sdc}")
                designs_found.setdefault(orfs_name, set()).add(orfs_library)

    for design, techs in orfs_designs.items():
        if design not in designs_found:
            print(f'Gallery does not contain design: {design} for {", ".join(techs)}')
        else:
            tech_diff = techs.difference(designs_found[design])
            if tech_diff:
                print(f'Gallery design {design} is missing for {", ".join(tech_diff)}')

    if not local:
        repo_dir.cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert ORFS to sc-gallery')
    parser.add_argument('--local', type=str, help='Path to local ORFS clone')
    parser.add_argument('--mirror', action='store_true', help='Mirror sdc and rules files')
    args = parser.parse_args()

    convert_all(local=args.local,
                mirror=args.mirror)
