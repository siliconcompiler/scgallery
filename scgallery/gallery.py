#!/usr/bin/env python3
"""Main module for SiliconCompiler Gallery execution.

This script provides the main class and command-line interface for running
the SiliconCompiler Gallery, which automates the process of building a
collection of designs across various targets (PDKs and standard cell libraries).
"""

import argparse
import json
import os
import shutil
import sys
import threading
import fnmatch
import os.path
from collections.abc import Container
from typing import Callable, List, Tuple, Dict, Union, Optional, Iterable

import siliconcompiler
from siliconcompiler import Design, Lint, ASIC
from siliconcompiler.schema.parametertype import NodeType
from siliconcompiler.utils import default_credentials_file, paths, curation

from scgallery.targets.freepdk45 import nangate45 as freepdk45_nangate45
from scgallery.targets.gf180 import (
    gf180mcu_fd_sc_mcu7t5v0 as gf180_gf180mcu_fd_sc_mcu7t5v0,
    gf180mcu_fd_sc_mcu9t5v0 as gf180_gf180mcu_fd_sc_mcu9t5v0,
)
from scgallery.targets.asap7 import asap7sc7p5t_rvt as asap7_asap7sc7p5t_rvt
from scgallery.targets.skywater130 import sky130hd as sky130_sky130hd
from scgallery.targets.ihp130 import sg13g2_stdcell as ihp130_sg13g2_stdcell
from scgallery.targets.linting import lint as gallery_lint
from siliconcompiler.flows.lintflow import LintFlow
from scgallery import __version__


class Gallery:
    """A class for managing and running a gallery of hardware designs.

    The Gallery class is the main driver for running a set of designs against
    a set of targets. It handles configuration, setup, execution (local or
    remote), and result summarization.

    Args:
        name (str, optional): An optional name for the gallery instance.
            Defaults to None.
        path (str, optional): The root directory for gallery outputs.
            Defaults to './gallery-<name>/<sc-version>/'.
    """

    def __init__(self, name: Optional[str] = None, path: Optional[str] = None):
        """Initializes a new Gallery instance."""
        self.__name = name
        self.set_path(path)

        self.__targets: Dict[str, Callable[[Union[ASIC, Lint]], None]] = {}
        for name, target in (
                ("freepdk45_nangate45", freepdk45_nangate45),
                ("skywater130_sky130hd", sky130_sky130hd),
                ("asap7_asap7sc7p5t_rvt", asap7_asap7sc7p5t_rvt),
                ("gf180_gf180mcu_fd_sc_mcu9t5v0", gf180_gf180mcu_fd_sc_mcu9t5v0),
                ("gf180_gf180mcu_fd_sc_mcu7t5v0", gf180_gf180mcu_fd_sc_mcu7t5v0),
                ("ihp130_sg13g2_stdcell", ihp130_sg13g2_stdcell)):
            self.add_target(name, target)

        self.__designs: Dict[str, Design] = {}
        from scgallery import designs
        for design in designs.all_designs():
            self.add_design(getattr(designs, design)())

        self.__run_config = {
            "targets": set(),
            "designs": set()
        }

        self.__status = []
        self.__report_chips = {}

        self.set_jobname_suffix(None)
        self.set_clean(False)
        self.set_remote(None)
        self.set_scheduler(None)

    @property
    def name(self) -> Union[str, None]:
        """Name of the gallery."""
        return self.__name

    @property
    def has_name(self) -> bool:
        """Determines if the gallery has a name."""
        return self.name is not None

    @property
    def title(self) -> str:
        """Title string for the gallery."""
        name = "Gallery"
        if self.has_name:
            name = f"{self.name} gallery"
        return f"{name} generator for SiliconCompiler {siliconcompiler.__version__}"

    @property
    def path(self) -> str:
        """Absolute path to the gallery's output directory."""
        return self.__path

    def set_path(self, path: Optional[str]) -> None:
        """Sets the path for the gallery output.

        The path will be converted to an absolute path. If no path is provided,
        a default is generated based on the current working directory, gallery
        name, and SiliconCompiler version.

        Args:
            path (str): Path to the gallery output directory.
        """
        if not path:
            default_path = 'gallery'
            if self.has_name:
                default_path = f'{default_path}-{self.name}'
            path = os.path.join(os.getcwd(),
                                default_path,
                                siliconcompiler.__version__)
        self.__path = os.path.abspath(path)

    def add_target(self, name: str, func: Callable[[Union[ASIC, Lint]], None]) -> None:
        """Adds a target setup module to the gallery.

        Args:
            name (str): The name of the target.
            func (Callable): The setup function for the target.
        """
        self.__targets[name] = func

    def remove_target(self, name: str) -> None:
        """Removes a target from the gallery.

        Args:
            name (str): The name of the target to remove.
        """
        if name in self.__targets:
            del self.__targets[name]

    def get_targets(self) -> List[str]:
        """Gets a list of target names registered in the gallery.

        Returns:
            List[str]: A list of target names.
        """
        return list(self.__targets.keys())

    def add_design(self, design: Design) -> None:
        """Adds a design to the gallery.

        Args:
            design (Design): The design object.
        """
        self.__designs[design.name] = design

    def remove_design(self, name: str) -> None:
        """Removes a design from the gallery.

        Args:
            name (str): The name of the design to remove.
        """
        if name in self.__designs:
            del self.__designs[name]

    def get_design(self, design: str) -> Design:
        """Gets the configuration for a specific design.

        Args:
            design (str): The name of the design.

        Returns:
            Design: The design object.
        """
        return self.__designs[design]

    def get_designs(self) -> List[str]:
        """Gets a sorted list of design names registered in the gallery.

        Returns:
            List[str]: A sorted list of design names.
        """
        return sorted(list(self.__designs.keys()))

    def set_remote(self, remote: Optional[str]) -> None:
        """Sets the path to the remote credentials file.

        Args:
            remote (str): Path to the credentials file.

        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        if remote:
            remote = os.path.abspath(remote)
            if not os.path.isfile(remote):
                raise FileNotFoundError(f'{remote} does not exist or is not a regular file')
        self.__remote = remote

    @property
    def is_remote(self) -> bool:
        """Determines if the gallery is set to run remotely."""
        return self.__remote is not None

    def set_scheduler(self, scheduler: Optional[str]) -> None:
        """Sets the scheduler to use for job execution.

        Args:
            scheduler (str): The name of the scheduler (e.g., 'slurm').
        """
        self.__scheduler = scheduler

    @property
    def has_scheduler(self) -> bool:
        """Determines if a scheduler is set."""
        return self.__scheduler is not None

    @property
    def scheduler(self) -> Union[str, None]:
        """Gets the name of the scheduler."""
        return self.__scheduler

    def set_clean(self, clean: bool) -> None:
        """Sets whether the gallery should clean previous run directories.

        Args:
            clean (bool): If True, enables cleaning.
        """
        self.__clean = clean

    @property
    def is_clean(self) -> bool:
        """Determines if the gallery is set to clean previous run directories."""
        return self.__clean

    def set_jobname_suffix(self, suffix: Optional[str]) -> None:
        """Sets a suffix to append to default job names.

        Args:
            suffix (str): The string to append to job names.
        """
        self.__jobname = suffix

    def set_run_designs(self, designs: Iterable[str]) -> None:
        """Sets the designs to execute during a run.

        Args:
            designs (List[str]): A list of design names.
        """
        self.__run_config['designs'].clear()
        self.__run_config['designs'].update(designs)

    def set_run_targets(self, targets: Iterable[str]) -> None:
        """Sets the targets to use during a run.

        Args:
            targets (List[str]): A list of target names.
        """
        self.__run_config['targets'].clear()
        self.__run_config['targets'].update(targets)

    def __setup_design(self, design: str, target: str) -> Tuple[Union[Lint, ASIC], bool]:
        """Prepares a project object for a given design and target.

        Args:
            design (str): The name of the design.
            target (str): The name of the target.

        Returns:
            Tuple[Union[Lint, ASIC], bool]: A tuple containing the configured
            project object and a boolean indicating if the setup is valid
            for a run (e.g., has SDC files).
        """
        from scgallery import GalleryDesign

        print(f'Setting up "{design}" with "{target}"')
        design_obj = self.__designs[design]
        is_lint = target == "lint"

        project = Lint(design_obj) if is_lint else ASIC(design_obj)
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
                         jobsuffix: Optional[str] = None) -> None:
        """Configures common run options for a project.

        Args:
            project (Union[ASIC, Lint]): The project object to configure.
            jobsuffix (str, optional): An optional suffix for the job name.
        """
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
            project.option.scheduler.set_name(self.scheduler)
        elif self.is_remote:
            project.option.set_credentials(self.__remote)
            project.option.set_remote(True)

    def __lint(self, design: Dict, tool: str) -> Union[bool, None]:
        """Runs the linting flow for a given design.

        Args:
            design (Dict): A dictionary containing project information.
            tool (str): The linting tool to use ('verilator' or 'slang').

        Returns:
            Union[bool, None]: True if linting passes with zero errors,
            False otherwise. None if no project is configured.
        """
        project = design['project']

        if not project:
            return None

        project.set_flow(LintFlow("scgallery-lint", tool=tool))
        self.__setup_run_chip(project, jobsuffix="_lint")

        try:
            project.run()
        except Exception:
            project.logger.exception("Lint failed with exception")
            return False

        errors = project.history(project.option.get_jobname()).get('metric', 'errors',
                                                                   step='lint', index='0')
        return errors == 0

    def __run_design(self, design: Dict) -> Tuple[Union[ASIC, Lint], bool]:
        """Executes the main flow for a design.

        Args:
            design (Dict): A dictionary containing project information.

        Returns:
            Tuple[Union[ASIC, Lint], bool]: The project object and a boolean
            indicating if the run succeeded.
        """
        project: Union[Lint, ASIC] = design['project']
        self.__setup_run_chip(project)

        try:
            project.run()
            return project, True
        except Exception:
            project.logger.exception("Run failed with exception")
            return project, False

    def __finalize(self, design: str, project: ASIC, succeeded: bool) -> None:
        """Finalizes a run, processing results and updating status.

        Args:
            design (str): The name of the design.
            project (ASIC): The project object from the run.
            succeeded (bool): Whether the run completed without exceptions.
        """
        report_data = {
            "project": project,
            "platform": project.get('asic', 'pdk')
        }
        self.__report_chips.setdefault(design, []).append(report_data)

        if succeeded:
            project.summary()
            project.snapshot(display=False)

        self.__status.append({
            "design": design,
            "pdk": project.get('asic', 'pdk'),
            "mainlib": project.get('asic', 'mainlib'),
            "error": not succeeded,
            "project": project
        })

        if not succeeded:
            project.logger.error("Run failed")
        else:
            project.logger.info("Run succeeded")

        self.__copy_project_data(project, report_data)

    def __copy_project_data(self, project: ASIC, report_data: Dict) -> None:
        """Copies key artifacts from a run to the gallery directory.

        Args:
            project (ASIC): The project object.
            report_data (Dict): A dictionary to store report metadata.
        """
        jobname = project.option.get_jobname()
        png_source = os.path.join(paths.jobdir(project), f'{project.name}.png')
        file_root = f'{project.name}_{jobname}'

        if os.path.isfile(png_source):
            img_dest = os.path.join(self.path, f'{file_root}.png')
            shutil.copy(png_source, img_dest)
            report_data["path"] = img_dest

        curation.archive(project,
                         include=['reports', '*.log'],
                         archive_name=os.path.join(self.path, f'{file_root}.tgz'))

    def __get_runnable_jobs(self) -> List[Dict]:
        """Generates a sorted list of jobs to be executed.

        Returns:
            List[Dict]: A list of job dictionaries, each ready for execution.
        """
        regular_jobs = []

        def _run_setup(design, target):
            project, valid = self.__setup_design(design, target)
            if not valid:
                return

            print_text = f'Running "{design}" with "{target}"'
            regular_jobs.append({
                "print": print_text,
                "design": design,
                "project": project,
                "target": target
            })

        config_threads = [
            threading.Thread(target=_run_setup, args=(design, target))
            for design in self.__run_config['designs']
            if design in self.__designs
            for target in self.__run_config['targets']
        ]

        for thread in config_threads:
            thread.start()
        for thread in config_threads:
            thread.join()

        return sorted(regular_jobs, key=lambda x: x["print"])

    def get_run_report(self) -> Dict:
        """Returns a report of the completed runs.

        Returns:
            Dict: A dictionary containing run data.
        """
        return self.__report_chips.copy()

    def lint(self, tool: str) -> bool:
        """Runs lint on all enabled designs.

        Args:
            tool (str): The linting tool to use.

        Returns:
            bool: True if all designs pass linting, False otherwise.
        """
        status = {}
        has_error = False
        for job in self.__get_runnable_jobs():
            print(job['print'])
            lint_status = self.__lint(job, tool)
            if lint_status is not None:
                has_error |= not lint_status
                status[job['design'], job['target']] = lint_status

        for (design, target), result in status.items():
            title = f"Lint on \"{design}\" with \"{target}\""
            print(f"{title}: {'Passed' if result else 'Failed'}")

        return not has_error

    def run(self) -> bool:
        """Executes the main gallery run.

        Iterates over the configured designs and targets, runs the SiliconCompiler
        flow, and generates summaries.

        Returns:
            bool: True if all runs succeed, False otherwise.
        """
        os.makedirs(self.path, exist_ok=True)
        self.__status.clear()
        self.__report_chips.clear()

        jobs_to_run = self.__get_runnable_jobs()
        if not jobs_to_run:
            print("No valid jobs to run.")
            return False

        if self.is_remote:
            def _run_remote(job):
                project, succeeded = self.__run_design(job)
                self.__finalize(job['design'], project, succeeded)

            threads = [threading.Thread(target=_run_remote, args=(job,)) for job in jobs_to_run]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        else:
            for job in jobs_to_run:
                print(job['print'])
                project, succeeded = self.__run_design(job)
                self.__finalize(job['design'], project, succeeded)

        self.summary()
        return not any(data["error"] for data in self.__status)

    def summary(self) -> None:
        """Prints a summary of the previous run."""
        print("Run summary:")
        overall_passed = True
        for status in self.__status:
            print(f"  Design: {status['project'].name} on {status['pdk']} "
                  f"with mainlib {status['mainlib']}")
            if status['error']:
                overall_passed = False
                print("    Status: Failed")
            else:
                print("    Status: Passed")
        print(f"Overall result: {'Passed' if overall_passed else 'Failed'}")

    @classmethod
    def main(cls) -> int:
        """Main method for command-line invocation."""
        gallery = cls()

        class ArgChoiceGlob(Container):
            """Helper class to support glob matching in argparse choices."""

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
            """Formats a list into wrapped lines for help text."""
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
            gallery.add_target("lint", gallery_lint)
            gallery.set_run_targets(["lint"])

            if gallery.lint(args.lint_tool):
                return 0

            return 1

        if not gallery.run():
            return 1
        return 0


if __name__ == "__main__":
    sys.exit(Gallery.main())
