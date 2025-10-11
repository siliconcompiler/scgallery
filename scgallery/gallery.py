#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import sys
import threading
import fnmatch

import os.path

from collections.abc import Container
from typing import Callable, List, Tuple, Dict, Union

import siliconcompiler
from siliconcompiler import Design, Lint, ASIC
from siliconcompiler.schema.parametertype import NodeType
from siliconcompiler.utils import default_credentials_file
from siliconcompiler.utils import paths, curation

from scgallery.targets.freepdk45 import (
    nangate45 as freepdk45_nangate45
)
from scgallery.targets.gf180 import (
    gf180mcu_fd_sc_mcu7t5v0 as gf180_gf180mcu_fd_sc_mcu7t5v0,
    gf180mcu_fd_sc_mcu9t5v0 as gf180_gf180mcu_fd_sc_mcu9t5v0
)
from scgallery.targets.asap7 import (
    asap7sc7p5t_rvt as asap7_asap7sc7p5t_rvt
)
from scgallery.targets.skywater130 import (
    sky130hd as sky130_sky130hd
)
from scgallery.targets.ihp130 import (
    sg13g2_stdcell as ihp130_sg13g2_stdcell
)
from scgallery.targets.linting import lint as gallery_lint

from siliconcompiler.flows.lintflow import LintFlow

from scgallery import __version__

# from scgallery.checklists import asicflow_rules


class Gallery:
    def __init__(self, name=None, path=None):
        self.__name = name
        self.set_path(path)

        self.__targets = {}
        for name, target in (
                ("freepdk45_nangate45", freepdk45_nangate45),
                ("skywater130_sky130hd", sky130_sky130hd),
                ("asap7_asap7sc7p5t_rvt", asap7_asap7sc7p5t_rvt),
                ("gf180_gf180mcu_fd_sc_mcu9t5v0", gf180_gf180mcu_fd_sc_mcu9t5v0),
                ("gf180_gf180mcu_fd_sc_mcu7t5v0", gf180_gf180mcu_fd_sc_mcu7t5v0),
                ("ihp130_sg13g2_stdcell", ihp130_sg13g2_stdcell),
                ("None", None)):
            self.add_target(name, target)

        self.__designs = {}
        from scgallery.designs import all_designs as sc_all_designs
        for name, design in sc_all_designs().items():
            self.add_design(name, design())

        self.__run_config = {
            "targets": set(),
            "designs": set()
        }

        self.__status = []
        self.__report_chips = {}

        self.__jobname = None
        self.set_clean(False)
        self.set_remote(None)
        self.set_scheduler(None)

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
    def add_target(self, name: str, func: Callable):
        '''
        Add a target to the gallery.

        Parameters:
            name (str): name of the target
            func (module): python module for the target
        '''
        self.__targets[name] = func

    def remove_target(self, name: str):
        '''
        Removes a target from the gallery.

        Parameters:
            name (str): name of the target to remove
        '''
        if name in self.__targets:
            del self.__targets[name]

    def get_targets(self) -> List[Callable]:
        '''
        Get a list of target names registered in the gallery.

        Returns:
            list (str): List of target names
        '''
        return list(self.__targets.keys())

    #######################################################
    def add_design(self, name: str, design: Design):
        '''
        Add a design to the gallery.

        Parameters:
            name (str): name of the design
            module (module): python module for the design
            rules (list [path]): list of paths to the rules for this design
            setup (list [function]): list of functions to help configure the design in external
                galleries
        '''
        self.__designs[name] = design

    def remove_design(self, name: str):
        '''
        Removes a design from the gallery.

        Parameters:
            name (str): name of the design to remove
        '''
        if name in self.__designs:
            del self.__designs[name]

    def get_design(self, design: str) -> Design:
        '''
        Gets the configuration for a design.

        Returns:
            dict: Configuration of a design
        '''
        return self.__designs[design]

    def get_designs(self) -> List[str]:
        '''
        Get a list of design names registered in the gallery.

        Returns:
            list (str): List of design names
        '''
        return sorted(list(self.__designs.keys()))

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
    def set_scheduler(self, scheduler):
        '''
        Set the scheduler to use.

        Parameters:
            scheduler (str): scheduler name
        '''
        self.__scheduler = scheduler

    @property
    def has_scheduler(self):
        '''
        Determine if a scheduler is set

        Returns:
            boolean: True, is scheduler is set
        '''
        return self.__scheduler is not None

    @property
    def scheduler(self):
        '''
        Get the name of the scheduler

        Returns:
            str: name of scheduler
        '''
        return self.__scheduler

    #######################################################
    def set_clean(self, clean):
        '''
        Set if the gallery should clean a previous run.

        Parameters:
            clean (boolean): Flag to indicate if clean should be used
        '''
        if clean:
            clean = True
        else:
            clean = False
        self.__clean = clean

    @property
    def is_clean(self):
        '''
        Determine if the gallery is set to clean a previous run

        Returns:
            boolean: True, if resuming, False if not
        '''
        return self.__clean

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
        self.__run_config['designs'].update(designs)

    #######################################################
    def set_run_targets(self, targets):
        '''
        Sets the targets to use during a run.

        Parameters:
            targets (list [str]): list of target names
        '''
        self.__run_config['targets'].clear()
        self.__run_config['targets'].update(targets)

    #######################################################
    def __setup_design(self, design, target) -> Tuple[Union[Lint, ASIC], bool]:
        from scgallery import GalleryDesign

        print(f'Setting up "{design}" with "{target}"')
        design_obj = self.__designs[design]
        is_lint = target == "lint"

        if is_lint:
            project = Lint(design_obj)
        else:
            project = ASIC(design_obj)
        project.add_fileset("rtl")

        self.__targets[target](project)

        if isinstance(design_obj, GalleryDesign):
            design_obj.process_setups(target, project)

        has_sdc = False
        if not is_lint:
            mainlib = project.get("asic", "mainlib")
            has_sdc = design_obj.has_fileset(f"sdc.{mainlib}")

        is_valid = has_sdc or is_lint

        return project, is_valid

    def __setup_run_chip(self,
                         project: Union[ASIC, Lint],
                         name: str,
                         jobsuffix: str = None):
        if isinstance(project, ASIC):
            pdk = project.get('asic', 'pdk')
            mainlib = project.get('asic', 'mainlib')
            project.add_fileset(f"sdc.{mainlib}")
            jobname = f"{pdk}_{mainlib}"
        else:
            jobname = "lint"

        if self.__jobname:
            jobname += f"_{self.__jobname}"
        if jobsuffix:
            jobname += jobsuffix

        project.option.set_jobname(jobname)

        project.option.set_nodisplay(True)
        project.option.set_nodashboard(True)
        project.option.set_autoissue(True)
        project.option.set_quiet(True)
        project.option.set_clean(self.is_clean)

        if self.has_scheduler:
            project.option.scheduler.set_name(self.__scheduler)
        elif self.is_remote:
            project.option.set_credentials(self.__remote)
            project.option.set_remote(True)

    def __lint(self, design, tool):
        project = design['project']

        if not project:
            # custom flow, so accept
            return None

        project.set_flow(LintFlow("scgallery-lint", tool=tool))

        self.__setup_run_chip(project, design["design"], jobsuffix="_lint")

        try:
            project.run(raise_exception=True)
        except Exception:
            return False

        if project.history(project.option.get_jobname()).get('metric', 'errors',
                                                             step='lint', index='0') == 0:
            return True
        return False

    def __run_design(self, design: Dict) -> Tuple[ASIC, bool]:
        project = design['project']

        self.__setup_run_chip(project, design["design"])

        try:
            project.run()
        except Exception:
            return project, False

        return project, True

    def __finalize(self, design: str, project: ASIC, succeeded: bool):
        report_data = {
            "project": project,
            "platform": project.get('asic', 'pdk')
        }
        self.__report_chips.setdefault(design, []).append(report_data)

        if succeeded:
            project.summary()
            project.snapshot(display=False)
            error = None
        else:
            error = True

        self.__status.append({
            "design": design,
            "pdk": project.get('asic', 'pdk'),
            "mainlib": project.get('asic', 'mainlib'),
            "error": error,
            "project": project
        })
        if not succeeded:
            project.logger.error("Run failed")
        elif error:
            project.logger.error("Rules mismatch")
        else:
            project.logger.info("Rules match")

        self.__copy_project_data(project, report_data)

    def __copy_project_data(self, project: ASIC, report_data: Dict):
        jobname = project.option.get_jobname()
        png = os.path.join(paths.jobdir(project), f'{project.name}.png')

        file_root = f'{project.name}_{jobname}'

        if os.path.isfile(png):
            img_path = os.path.join(self.path, f'{file_root}.png')
            shutil.copy(png, img_path)
            report_data["path"] = img_path

        curation.archive(project,
                         include=['reports', '*.log'],
                         archive_name=os.path.join(self.path, f'{file_root}.tgz'))

    def __get_runnable_jobs(self):
        regular_jobs = []

        def _run_setup(design, target):
            project, valid = self.__setup_design(design, target)
            if not valid:
                return

            print_text = f'Running "{design}"'
            if target:
                print_text += f' with "{target}"'

            regular_jobs.append({
                "print": print_text,
                "design": design,
                "project": project,
                "target": target})

        config_jobs = []
        for design in self.__run_config['designs']:
            if design not in self.__designs:
                print(f'  Error: design "{design}" is not available in gallery')
                continue

            targets = self.__run_config['targets']
            targets = [target for target in targets if target != "None"]

            for target in targets:
                config_jobs.append(threading.Thread(
                    target=_run_setup,
                    args=(design, target)))

        # Start jobs in parallel
        for job in config_jobs:
            job.start()

        # Wait
        for job in config_jobs:
            if job.is_alive():
                job.join()

        return sorted(regular_jobs, key=lambda x: x["print"])

    def get_run_report(self):
        return self.__report_chips.copy()

    def lint(self, tool):
        '''
        Run lint on the enabled designs.
        '''

        status = {}

        error = False
        for job in self.__get_runnable_jobs():
            print(job['print'])
            lint_status = self.__lint(job, tool)
            if lint_status is not None:
                error |= not lint_status

                status[job['design'], job['target']] = lint_status

        for job, result in status.items():
            design, target = job

            title = f"Lint on \"{design}\""
            if target:
                title += f" with \"{target}\""

            print(title)
            if result:
                print("  Passed")
            else:
                print("  Failed")

        return not error

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

        regular_jobs = self.__get_runnable_jobs()

        if not regular_jobs:
            return False

        if self.is_remote:
            def _run_remote(chip, design, job):
                if not chip:
                    return
                chip, succeeded = self.__run_design(job)
                self.__finalize(design, chip, succeeded)

            jobs = [threading.Thread(
                target=_run_remote,
                args=(job['chip'], job['design'], job))
                for job in regular_jobs]

            # Submit jobs in parallel
            for job in jobs:
                job.start()

            # Wait
            for job in jobs:
                job.join()
        else:
            for job in regular_jobs:
                project = job['project']
                design = job['design']

                print(job['print'])
                project, succeeded = self.__run_design(job)
                self.__finalize(design, project, succeeded)

        self.summary()

        failed = any([data["error"] for data in self.__status])
        return not failed

    def summary(self):
        '''
        Print a summary of the previous run.
        '''
        print("Run summary:")
        failed = False
        for status in self.__status:
            print(f" Design: {status['project'].name} on {status['pdk']} pdk "
                  f"with mainlib {status['mainlib']}")
            error = status['error']
            if error:
                failed = True
                print("  Rules check failed")
            elif error is None:
                # Mark as failed since rules are missing
                failed = True
            else:
                print("  Rules check passed")
        if not failed:
            print('Run passed')

    @classmethod
    def main(cls):
        '''
        Main method to initiate the gallery from the commandline.
        '''
        gallery = cls()

        class ArgChoiceGlob(Container):
            def __init__(self, choices):
                super().__init__()

                self.__choices = set(choices)

            def __contains__(self, item):
                if item in self.__choices:
                    return True

                if fnmatch.filter(self.__choices, item):
                    return True

                return False

            def __iter__(self):
                return self.__choices.__iter__()

            def get_items(self, choices):
                items = set()
                for c in choices:
                    items.update(fnmatch.filter(self.__choices, c))
                return sorted(list(items))

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

        design_choices = ArgChoiceGlob(gallery.__designs.keys())
        target_choices = ArgChoiceGlob(gallery.__targets.keys())

        parser = argparse.ArgumentParser(
            prog='sc-gallery',
            description=description,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        parser.add_argument('-design',
                            action='append',
                            choices=design_choices,
                            metavar='<design>',
                            help='Name of design to run')

        parser.add_argument('-target',
                            action='append',
                            choices=target_choices,
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

        parser.add_argument('-scheduler',
                            choices=NodeType.parse(
                                ASIC().get('option', 'scheduler', 'name',
                                           field='type')).values,
                            help='Select the scheduler to use during exection')

        parser.add_argument('-clean',
                            action='store_true',
                            help='Use option,clean')

        parser.add_argument('-gallery',
                            metavar='<module>',
                            help='Python module for custom galleries')

        parser.add_argument('-skip_rules',
                            metavar='<rule>',
                            nargs='+',
                            help='List of regex names for rules to skip in checks')

        parser.add_argument('-json',
                            metavar='<path>',
                            help='Generate json matrix of designs and targets')

        parser.add_argument('-lint',
                            action='store_true',
                            help='Run lint only')

        parser.add_argument('-lint_tool',
                            choices=['verilator', 'slang'],
                            default='verilator',
                            help='Tool to use for linting')

        parser.add_argument('-version', action='version', version=__version__)

        args = parser.parse_args()

        gallery.set_path(args.path)
        gallery.set_clean(args.clean)
        gallery.set_remote(args.remote)

        if args.scheduler:
            gallery.set_scheduler(args.scheduler)

        if args.target:
            gallery.set_run_targets(target_choices.get_items(args.target))
        else:
            gallery.set_run_targets(gallery.__targets.keys())

        if args.design:
            gallery.set_run_designs(design_choices.get_items(args.design))
        else:
            gallery.set_run_designs(gallery.__designs.keys())

        if args.json:
            matrix = []
            for data in gallery.__get_runnable_jobs():
                matrix.append({"design": data["design"], "target": data["target"], "remote": False})

            if os.path.exists(args.json):
                json_matrix = []
                with open(args.json, 'r') as f:
                    json_matrix = json.load(f)

                spare_fields = ('skip', 'cache')
                for config in json_matrix:
                    has_extra = False
                    for key in spare_fields:
                        if key in config:
                            has_extra = True

                    if has_extra:
                        # Copy extra information
                        for new_config in matrix:
                            match = [
                                new_config[key] == config[key] for key in ('design',
                                                                           'target')
                            ]
                            if all(match):
                                if 'skip' in config:
                                    new_config['cache'] = False
                                for key, value in config.items():
                                    new_config[key] = value

            with open(args.json, 'w') as f:
                json.dump(matrix, f, indent=4, sort_keys=True)
            return 0

        if args.lint:
            gallery.add_target("lint", gallery_lint.setup)
            gallery.set_run_targets(["lint"])

            if gallery.lint(args.lint_tool):
                return 0

            return 1

        if not gallery.run():
            return 1
        return 0


if __name__ == "__main__":
    sys.exit(Gallery.main())
