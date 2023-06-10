#!/usr/bin/env python3

import os
import shutil
import argparse
import json

import siliconcompiler
from siliconcompiler.targets import asap7_demo, freepdk45_demo, skywater130_demo

from scgallery.designs import all_designs


def __design_has_runner(design):
    return getattr(design, 'run', None) is not None


def __copy_chip_image(chip, gallery):
    if not chip:
        return
    jobname = chip.get('option', 'jobname')
    png = os.path.join(chip._getworkdir(),
                       f'{chip.design}.png')
    if os.path.isfile(png):
        shutil.copy(png, os.path.join(gallery, f'{chip.design}_{jobname}.png'))


def __setup_design(design, target):
    try:
        chip = design.setup(target=target)
        return chip
    except FileNotFoundError as e:
        print(e)
        return None


def run_design(chip):
    jobname = chip.get('option', 'target').split('.')[-1]
    chip.set('option', 'jobname', f"{chip.get('option', 'jobname')}_{jobname}")

    chip.set('option', 'nodisplay', True)
    chip.set('option', 'resume', True)

    try:
        chip.run()
        chip.summary()
    except Exception:
        return None

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
                        default=os.path.join('images', siliconcompiler.__version__))

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
        exit(0)

    gallery = os.path.abspath(args.gallery)
    os.makedirs(gallery, exist_ok=True)

    for _, design in designs.items():
        print(f'Running {design.__name__}')
        if __design_has_runner(design):
            run = getattr(design, 'run')
            try:
                chip = run()
                __copy_chip_image(chip, gallery)
            except Exception:
                pass
        else:
            for _, target in targets.items():
                chip = __setup_design(design, target)
                chip = run_design(chip)
                __copy_chip_image(chip, gallery)
