#!/usr/bin/env python3

import os
import shutil
import argparse
import json
import sys

import siliconcompiler
from siliconcompiler.targets import asap7_demo, freepdk45_demo, skywater130_demo

from scgallery.designs import all_designs


def __design_has_runner(design):
    return getattr(design, 'run', None) is not None


def __copy_chip_data(chip, gallery):
    if not chip:
        return
    jobname = chip.get('option', 'jobname')
    png = os.path.join(chip._getworkdir(),
                       f'{chip.design}.png')

    file_root = f'{chip.design}_{jobname}'

    if os.path.isfile(png):
        shutil.copy(png, os.path.join(gallery, f'{file_root}.png'))

    chip.archive(include=['reports', '*.log'],
                 archive_name=os.path.join(gallery, f'{file_root}.tgz'))


def __setup_design(design, target):
    try:
        chip = design.setup(target=target)
        return chip
    except FileNotFoundError as e:
        print(f'{design} for {target} threw an error: {e}')
        return None


def run_design(chip):
    jobname = chip.get('option', 'target').split('.')[-1]
    chip.set('option', 'jobname', f"{chip.get('option', 'jobname')}_{jobname}")

    chip.set('option', 'nodisplay', True)

    try:
        chip.run()
        chip.summary()
    except Exception:
        return chip

    return chip


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='scgallery',
        description='Gallery generator for SiliconCompiler'
    )

    parser.add_argument('-design',
                        choices=sorted(all_designs().keys()),
                        metavar='<design>',
                        help='Name of design to run')

    all_targets = {
        "freepdk45_demo": freepdk45_demo,
        "skywater130_demo": skywater130_demo,
        "asap7_demo": asap7_demo
    }

    parser.add_argument('-target',
                        choices=sorted(all_targets.keys()),
                        metavar='<target>',
                        help='Name of target to run')

    parser.add_argument('-gallery',
                        metavar='<path>',
                        help='Path to the gallery',
                        default=os.path.join('gallery', siliconcompiler.__version__))

    parser.add_argument('-json',
                        metavar='<path>',
                        help='Record a github usable json matrix')

    args = parser.parse_args()

    designs = all_designs()
    if args.design:
        designs = {args.design: designs[args.design]}

    targets = all_targets
    if args.target:
        targets = {args.target: all_targets[args.target]}

    if args.json:
        matrix = {'include': []}
        for design, design_obj in designs.items():
            if not __design_has_runner(design_obj):
                for target, target_obj in targets.items():
                    chip = __setup_design(design_obj, target_obj)
                    if chip:
                        matrix['include'].append({
                            'design': design,
                            'target': target
                        })
            else:
                matrix['include'].append({
                    'design': design,
                    'target': list(targets.keys())[0]
                })
        with open(args.json, 'w') as f:
            if matrix['include']:
                f.write(json.dumps(matrix))
            else:
                f.write('{}')
        sys.exit(0)

    gallery = os.path.abspath(args.gallery)
    os.makedirs(gallery, exist_ok=True)

    any_failed = False

    for _, design in designs.items():
        print(f'Running {design.__name__}')
        if __design_has_runner(design):
            run = getattr(design, 'run')
            try:
                chip = run()
                if not chip:
                    any_failed = True
                __copy_chip_data(chip, gallery)
            except Exception:
                pass
        else:
            for _, target in targets.items():
                chip = __setup_design(design, target)
                chip = run_design(chip)
                if not chip:
                    any_failed = True
                __copy_chip_data(chip, gallery)

    if any_failed:
        sys.exit(1)
    else:
        sys.exit(0)
