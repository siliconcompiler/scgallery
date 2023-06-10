#!/usr/bin/env python3

import argparse
import os
import shutil
import sys
import threading

import siliconcompiler
from siliconcompiler.utils import default_credentials_file
from siliconcompiler.targets import asap7_demo, freepdk45_demo, skywater130_demo

from scgallery.designs import all_designs as sc_all_designs
from scgallery.rules import check_rules
from scgallery import report


class Gallery:
    def __init__(self, name=None, path=None):
        self.__name = name
        self.set_path(path)

        self.__targets = {}
        for name, target in (("freepdk45_demo", freepdk45_demo),
                             ("skywater130_demo", skywater130_demo),
                             ("asap7_demo", asap7_demo)):
            self.add_target(name, target)

        self.__designs = {}
        for name, design in sc_all_designs().items():
            self.add_design(name, design["module"], rules=design["rules"])

        self.__run_config = {
            "targets": set(),
            "designs": set()
        }

        self.__status = []
        self.__report_chips = {}

        self.__jobname = None
        self.set_resume(False)
        self.set_remote(None)

    #######################################################
    @property
    def name(self):
        '''
        Name of the gallery

        Returns:
            str/None: Name of gallery
        '''
        return self.__name

    @property
    def has_name(self):
        '''
        Determine if the gallery has a name

        Returns:
            boolean: True, if a name is present, False if not
        '''
        if self.name:
            return True
        return False

    @property
    def title(self):
        '''
        Title string for the gallery

        Returns:
            str: Title for the gallery
        '''
        name = "Gallery"
        if self.has_name:
            name = f"{self.name} gallery"
        return f"{name} generator for SiliconCompiler {siliconcompiler.__version__}"

    #######################################################
    @property
    def path(self):
        '''
        Path to the gallery

        Returns:
            str: Absolute path to the gallery
        '''
        return self.__path

    def set_path(self, path):
        '''
        Set the path to the gallery.

        The path will be converted to an absolute path

        Parameters:
            path (str): path to the gallery output
        '''
        if not path:
            default_path = 'gallery'
            if self.has_name:
                default_path = f'{default_path}-{self.name}'
            path = os.path.join(os.getcwd(),
                                default_path,
                                siliconcompiler.__version__)
        self.__path = os.path.abspath(path)

    #######################################################
    def add_target(self, name, module):
        '''
        Add a target to the gallery.

        Parameters:
            name (str): name of the target
            module (module): python module for the target
        '''
        self.__targets[name] = module

    def remove_target(self, name):
        '''
        Removes a target from the gallery.

        Parameters:
            name (str): name of the target to remove
        '''
        if name in self.__targets:
            del self.__targets[name]

    def get_targets(self):
        '''
        Get a list of target names registered in the gallery.

        Returns:
            list (str): List of target names
        '''
        return list(self.__targets.keys())

    #######################################################
    def add_design(self, name, module, rules=None, setup=None):
        '''
        Add a design to the gallery.

        Parameters:
            name (str): name of the design
            module (module): python module for the design
            rules (list [path]): list of paths to the rules for this design
            setup (list [function]): list of functions to help configure the design in external
                galleries
        '''
        self.__designs[name] = {
            "module": module,
            "rules": [],
            "setup": []
        }

        if not rules:
            rules = []
        if not isinstance(rules, (list, tuple)):
            rules = [rules]
        for rule in rules:
            self.add_design_rule(name, rule)

        if not setup:
            setup = []
        if not isinstance(setup, (list, tuple)):
            setup = [setup]
        for func in setup:
            self.add_design_setup(name, func)

    def remove_design(self, name):
        '''
        Removes a design from the gallery.

        Parameters:
            name (str): name of the design to remove
        '''
        if name in self.__designs:
            del self.__designs[name]

    def get_design(self, design):
        '''
        Gets the configuration for a design.

        Returns:
            dict: Configuration of a design
        '''
        info = self.__designs[design].copy()
        for key in info.keys():
            if key == 'module':
                continue
            info[key] = info[key].copy()
        return info

    def get_designs(self):
        '''
        Get a list of design names registered in the gallery.

        Returns:
            list (str): List of design names
        '''
        return list(self.__designs.keys())

    #######################################################
    def set_remote(self, remote):
        '''
        Set the path to the remote credentials file.

        Parameters:
            remote (str): path to the credentials
        '''
        if remote:
            remote = os.path.abspath(remote)
            if not os.path.isfile(remote):
                raise FileNotFoundError(f'{remote} does not exists or is not a regular file')

        self.__remote = remote

    @property
    def is_remote(self):
        '''
        Determine if the gallery is set to run remotely

        Returns:
            boolean: True, if running remotely, False if not
        '''
        if self.__remote:
            return True
        return False

    #######################################################
    def set_resume(self, resume):
        '''
        Set if the gallery should resume a previous run.

        Parameters:
            resume (boolean): Flag to indicate if resume should be used
        '''
        if resume:
            resume = True
        else:
            resume = False
        self.__resume = resume

    @property
    def is_resume(self):
        '''
        Determine if the gallery is set to resume a previous run

        Returns:
            boolean: True, if resuming, False if not
        '''
        return self.__resume

    #######################################################
    def add_design_rule(self, design, rule):
        '''
        Add a new rules file to a design.

        Parameters:
            design (str): name of the design
            rule (path): path to the rules for this design
        '''
        if not rule:
            return

        if not os.path.isfile(rule):
            raise FileNotFoundError(rule)

        self.__designs[design]['rules'].append(rule)

    def get_design_rules(self, design):
        '''
        Get a list of rules for the design.

        Parameters:
            design (str): name of the design

        Returns:
            list (path): list of paths to rules files
        '''
        return self.__designs[design]['rules'].copy()

    def clear_design_rules(self, design):
        '''
        Removes all design rules from a design.

        Parameters:
            design (str): name of the design
        '''
        self.__designs[design]['rules'].clear()

    #######################################################
    def add_design_setup(self, design, func):
        '''
        Add a new setup function to a design.

        Parameters:
            name (str): name of the design
            setup (function): functions to help configure the design in external
                galleries
        '''
        self.__designs[design]['setup'].append(func)

    def get_design_setup(self, design):
        '''
        Get a list of setup functions to a design.

        Parameters:
            name (str): name of the design

        Returns:
            list (function): list of functions to setup the design
        '''
        return self.__designs[design]['setup'].copy()

    #######################################################
    def set_jobname_suffix(self, suffix):
        '''
        Sets a suffix to the default job names.

        Parameters:
            suffix (str): string to append to the job names during a gallery run.
        '''
        self.__jobname = suffix

    #######################################################
    def set_run_designs(self, designs):
        '''
        Sets the designs to execute during a run.

        Parameters:
            designs (list [str]): list of design names
        '''
        self.__run_config['designs'].clear()
        self.__run_config['designs'].update(designs.keys())

    def set_run_targets(self, targets):
        '''
        Sets the targets to use during a run.

        Parameters:
            targets (list [str]): list of target names
        '''
        self.__run_config['targets'].clear()
        self.__run_config['targets'].update(targets.keys())

    def __setup_design(self, design, target):
        print(f'Setting up "{design}" with "{target}"')
        chip = self.__designs[design]['module'].setup(
            target=self.__targets[target])

        # Perform additional setup functions
        if self.__designs[design]['setup']:
            for setup_func in self.__designs[design]['setup']:
                setup_func(chip)

        # Reject if no SDC is provided
        if not chip.valid('input', 'constraint', 'sdc'):
            return chip, False

        # Reject of SDC cannot be found
        sdcs = [sdc for sdc in chip.find_files('input', 'constraint', 'sdc', missing_ok=True)
                if sdc]
        if not sdcs:
            return chip, False

        return chip, True

    def __run_design(self, chip):
        jobname = chip.get('option', 'target').split('.')[-1]
        if self.__jobname:
            jobname += f"_{self.__jobname}"
        chip.set('option', 'jobname', f"{chip.get('option', 'jobname')}_{jobname}")

        chip.set('option', 'nodisplay', True)
        chip.set('option', 'quiet', True)

        chip.set('option', 'resume', self.is_resume)

        if self.is_remote:
            chip.set('option', 'credentials', self.__remote)
            chip.set('option', 'remote', True)

        try:
            chip.run()
        except Exception:
            return chip

        return chip

    def __finalize(self, design, chip):
        if not chip:
            return

        report_data = {
            "chip": chip,
            "platform": chip.get('option', 'pdk'),
            "rules": []
        }
        self.__report_chips.setdefault(design, []).append(report_data)

        chip.summary()

        rules_files = self.__designs[design]['rules']

        if rules_files:
            chip.logger.info(f"Checking rules in: {', '.join(rules_files)}")
            errors = check_rules(chip, rules_files)
            report_data["rules"] = errors
            for error in errors:
                chip.logger.error(error)
        else:
            errors = None

        self.__status.append({
            "design": design,
            "pdk": chip.get('option', 'pdk'),
            "mainlib": chip.get('asic', 'logiclib')[0],
            "errors": errors,
            "chip": chip
        })
        if errors:
            chip.logger.error("Rules mismatch")
        elif rules_files:
            chip.logger.info("Rules match")

        self.__copy_chip_data(chip, report_data)

    def __copy_chip_data(self, chip, report_data):
        jobname = chip.get('option', 'jobname')
        png = os.path.join(chip._getworkdir(), f'{chip.design}.png')

        file_root = f'{chip.design}_{jobname}'

        if os.path.isfile(png):
            img_path = os.path.join(self.path, f'{file_root}.png')
            shutil.copy(png, img_path)
            report_data["path"] = img_path

        chip.archive(include=['reports', '*.log'],
                     archive_name=os.path.join(self.path, f'{file_root}.tgz'))

    def __design_has_runner(self, design):
        return getattr(self.__designs[design]['module'], 'run', None) is not None

    def run(self):
        '''
        Main run function which will iterate over the design gallery and generate images and
        summaries for the listed designs and targets.

        Returns:
            boolean: True, if all designs succeeded and no rules were violated, False otherwise.
        '''
        os.makedirs(self.path, exist_ok=True)

        self.__status.clear()
        self.__report_chips.clear()

        regular_jobs = []
        runner_jobs = []

        for design in self.__run_config['designs']:
            if design not in self.__designs:
                print('  Error: design is not available in gallery')
                continue

            if self.__design_has_runner(design):
                runner_jobs.append({'print': f'Running "{design}"',
                                    "design": design})
            else:
                for target in self.__run_config['targets']:
                    chip, valid = self.__setup_design(design, target)
                    if not valid:
                        continue
                    regular_jobs.append({'print': f'Running "{design}" with "{target}"',
                                         "design": design,
                                         "chip": chip})

        runner_jobs = sorted(runner_jobs, key=lambda x: x["print"])
        regular_jobs = sorted(regular_jobs, key=lambda x: x["print"])

        if self.is_remote:
            def _run_remote(chip, design):
                chip = self.__run_design(chip)
                self.__finalize(design, chip)

            jobs = [threading.Thread(
                target=_run_remote,
                args=(job['chip'], job['design']))
                for job in regular_jobs]

            # Submit jobs in parallel
            for job in jobs:
                job.start()

            # Wait
            for job in jobs:
                job.join()
        else:
            for job in regular_jobs:
                chip = job['chip']
                design = job['design']

                print(job['print'])
                chip = self.__run_design(chip)
                self.__finalize(design, chip)

        for job in runner_jobs:
            runner_module = self.__designs[job['design']]['module']
            run = getattr(runner_module, 'run')
            try:
                chip = run()
                self.__finalize(design, chip)
            except Exception:
                pass

        # Generate overview
        overview_data = []
        for design, design_datas in self.__report_chips.items():
            for design_data in design_datas:
                if 'path' not in design_data:
                    continue
                overview_data.append({
                    "path": design_data["path"],
                    "platform": design_data["platform"],
                    "design": design
                })
        if overview_data:
            overview_file = 'overview'
            if self.__jobname:
                overview_file += f"_{self.__jobname}"
            report.generate_overview(self.title,
                                     overview_data,
                                     os.path.join(self.path,
                                                  f"{overview_file}.html"))

            # Generate detailed view
            detail_data = {}
            for design, design_datas in self.__report_chips.items():
                for design_data in design_datas:
                    detail_data.setdefault(design, []).append({
                        "chip": design_data['chip'],
                        "rules": design_data['rules']
                    })
            details_file = 'details'
            if self.__jobname:
                details_file += f"_{self.__jobname}"
            report.generate_details(self.title,
                                    detail_data,
                                    os.path.join(self.path, f"{details_file}.html"))

        self.summary()
        return not self.__status

    def summary(self):
        '''
        Print a summary of the previous run.
        '''
        print("Run summary:")
        failed = False
        for status in self.__status:
            print(f"Design: {status['chip'].design}")
            print(f"PDK: {status['pdk']}")
            print(f"Mainlib: {status['mainlib']}")
            errors = status['errors']
            if errors:
                failed = True
                for error in errors:
                    print(f"  {error}")
            else:
                print("  Passed")
        if not failed:
            print('Run passed')

    @classmethod
    def main(cls):
        '''
        Main method to initiate the gallery from the commandline.
        '''
        gallery = cls()

        def format_list(items, prefix_len, max_len=80):
            lines = []
            line = None
            while len(items) > 0:
                item = items[0]
                del items[0]
                if not line:
                    line = item
                else:
                    line += f", {item}"

                if len(line) > max_len:
                    lines.append(line)
                    line = None
            if line:
                lines.append(line)

            line_prefix = "".join(prefix_len * [" "])
            format_lines = []
            for n, line in enumerate(lines):
                if n > 0:
                    line = f"{line_prefix}{line}"
                format_lines.append(line)
            return "\n".join(format_lines)

        targets_help = format_list(gallery.get_targets(), 9)
        designs_help = format_list(gallery.get_designs(), 9)

        description = f'''
{gallery.title}

Targets: {targets_help}
Designs: {designs_help}
'''

        parser = argparse.ArgumentParser(
            prog='sc-gallery',
            description=description,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        parser.add_argument('-design',
                            action='append',
                            choices=sorted(gallery.__designs.keys()),
                            metavar='<design>',
                            help='Name of design to run')

        parser.add_argument('-target',
                            action='append',
                            choices=sorted(gallery.__targets.keys()),
                            metavar='<target>',
                            help='Name of target to run')

        parser.add_argument('-path',
                            metavar='<path>',
                            help='Path to the gallery',
                            default=gallery.path)

        parser.add_argument('-remote',
                            metavar='<path>',
                            nargs='?',
                            action='store',
                            const=default_credentials_file(),
                            default=None,
                            help='Perform a remote run, '
                                 'optionally provides path to remote credentials')

        parser.add_argument('-resume',
                            action='store_true',
                            help='Use option,resume')

        parser.add_argument('-gallery',
                            metavar='<module>',
                            help='Python module for custom galleries')

        args = parser.parse_args()

        gallery.set_path(args.path)
        gallery.set_resume(args.resume)
        gallery.set_remote(args.remote)

        if args.target:
            gallery.set_run_targets({target: gallery.__targets[target] for target in args.target})
        else:
            gallery.set_run_targets(gallery.__targets)

        if args.design:
            gallery.set_run_designs({design: gallery.__designs[design] for design in args.design})
        else:
            gallery.set_run_designs(gallery.__designs)

        if not gallery.run():
            return 1
        return 0


if __name__ == "__main__":
    sys.exit(Gallery.main())
