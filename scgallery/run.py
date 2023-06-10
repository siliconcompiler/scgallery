#!/usr/bin/env python3

import os
import shutil
import argparse

import siliconcompiler
from siliconcompiler.targets import asap7_demo, freepdk45_demo, skywater130_demo

from scgallery.designs import all_designs


def __design_has_runner(design):
    return getattr(design, 'run', None) is not None


def __copy_chip_image(chip, gallery):
    jobname = chip.get('option', 'jobname')
    png = os.path.join(chip._getworkdir(),
                       f'{chip.design}.png')
    if os.path.isfile(png):
        shutil.copy(png, os.path.join(gallery, f'{chip.design}_{jobname}.png'))


def run_design(design, target):
    try:
        chip = design.setup(target=target)
    except FileNotFoundError:
        return None

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

    args = parser.parse_args()

    gallery = os.path.abspath(args.gallery)
    os.makedirs(gallery, exist_ok=True)

    designs = list(all_designs().values())
    if args.design:
        print(all_designs(), args.design)
        designs = [all_designs()[args.design]]

    targets = list(all_targets.values())
    if args.target:
        designs = [all_targets[args.target]]

    for design in designs:
        if __design_has_runner(design):
            run = getattr(design, 'run')
            try:
                chip = run()
                __copy_chip_image(chip, gallery)
            except Exception:
                pass
        else:
            for target in targets:
                chip = run_design(design, target)
                __copy_chip_image(chip, gallery)
