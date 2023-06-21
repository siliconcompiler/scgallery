#!/usr/bin/env python3

import os
import shutil
import argparse
import sys

import siliconcompiler
from siliconcompiler.targets import asap7_demo, freepdk45_demo, skywater130_demo

from scgallery.designs import all_designs as sc_all_designs
from scgallery.rules import check_rules


class Gallery:

    def __init__(self, path=None):
        self.__path = path

        self.__targets = {
            "freepdk45_demo": freepdk45_demo,
            "skywater130_demo": skywater130_demo,
            "asap7_demo": asap7_demo
        }

        self.__designs = {
            **sc_all_designs()
        }

        self.__run_config = {
            "targets": set(),
            "designs": set()
        }

        self.__errors = []

    def set_gallery(self, path):
        self.__path = path

    def gallery(self):
        return os.path.abspath(self.__path)

    def add_target(self, name, module):
        self.__targets[name] = module

    def remove_target(self, name):
        if name in self.__targets:
            del self.__targets[name]

    def add_design(self, name, module):
        self.__designs[name] = module

    def remove_design(self, name):
        if name in self.__designs:
            del self.__designs[name]

    def argparse(self):
        parser = argparse.ArgumentParser(
            prog='scgallery',
            description='Gallery generator for SiliconCompiler'
        )

        parser.add_argument('-design',
                            choices=sorted(self.__designs.keys()),
                            metavar='<design>',
                            help='Name of design to run')

        parser.add_argument('-target',
                            choices=sorted(self.__targets.keys()),
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

        self.set_gallery(args.gallery)

        if args.target:
            self.set_run_targets({args.target: self.__targets[args.target]})
        else:
            self.set_run_targets(self.__targets)

        if args.design:
            self.set_run_designs({args.design: self.__designs[args.design]})
        else:
            self.set_run_designs(self.__designs)

    def set_run_designs(self, designs):
        self.__run_config['designs'].clear()
        self.__run_config['designs'].update(designs.values())

    def set_run_targets(self, targets):
        self.__run_config['targets'].clear()
        self.__run_config['targets'].update(targets.values())

    def _setup_design(self, design, target):
        try:
            chip = design.setup(target=target)
            return chip
        except FileNotFoundError as e:
            print(f'{design} for {target} threw an error: {e}')
            return None

    def __run_design(self, chip):
        jobname = chip.get('option', 'target').split('.')[-1]
        chip.set('option', 'jobname', f"{chip.get('option', 'jobname')}_{jobname}")

        chip.set('option', 'nodisplay', True)
        chip.set('option', 'quiet', True)
        chip.set('option', 'resume', True)

        try:
            chip.run()
        except Exception:
            return chip

        return chip

    def __finalize(self, design, chip):
        if not chip:
            return

        chip.summary()

        design_dir = os.path.dirname(design.__file__)
        rules_file = os.path.join(design_dir, 'rules.json')

        chip.logger.info(f"Checking rules in {rules_file}")
        try:
            errors = check_rules(chip, rules_file)
            for error in errors:
                chip.logger.error(error)
        except ValueError:
            errors = None

        if errors:
            self.__errors.append({
                "design": design,
                "pdk": chip.get('option', 'pdk'),
                "mainlib": chip.get('asic', 'logiclib')[0],
                "errors": errors
            })
            chip.logger.error("Rules mismatch")
        else:
            chip.logger.info("Rules match")

        self.__copy_chip_data(chip)

    def __copy_chip_data(self, chip):
        jobname = chip.get('option', 'jobname')
        png = os.path.join(chip._getworkdir(), f'{chip.design}.png')

        file_root = f'{chip.design}_{jobname}'

        if os.path.isfile(png):
            shutil.copy(png, os.path.join(self.gallery(), f'{file_root}.png'))

        chip.archive(include=['reports', '*.log'],
                     archive_name=os.path.join(self.gallery(), f'{file_root}.tgz'))

    def run(self):
        os.makedirs(self.gallery(), exist_ok=True)

        self.__errors.clear()
        any_failed = False

        for design in self.__run_config['designs']:
            print(f'Running {design.__name__}')
            if self.__design_has_runner(design):
                run = getattr(design, 'run')
                try:
                    chip = run()
                    if not chip:
                        any_failed = True
                    self.__finalize(design, chip)
                except Exception:
                    pass
            else:
                for target in self.__run_config['targets']:
                    chip = self._setup_design(design, target)
                    chip = self.__run_design(chip)
                    if not chip:
                        any_failed = True
                    self.__finalize(design, chip)

        self.summary()
        return not any_failed

    def summary(self):
        print("Run summary:")
        for failed in self.__errors:
            print(f"Design: {failed['design'].__name__}")
            print(f"PDK: {failed['pdk']}")
            print(f"Mainlib: {failed['mainlib']}")
            for error in failed['errors']:
                print(f"  {error}")
        if not self.__errors:
            print('Add passed')

    def __design_has_runner(self, module):
        return getattr(module, 'run', None) is not None


def main():
    gallery = Gallery()
    gallery.argparse()

    if not gallery.run():
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
