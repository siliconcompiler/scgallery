"""Defines a specialized Checklist for verifying ASIC flow results.

This module contains the ASICChecklist class, which is designed to parse
JSON-based rule files and construct a SiliconCompiler Checklist object. This
checklist can then be used to validate metrics from a completed ASIC flow run
against predefined criteria.
"""
import json
import fnmatch
from typing import Optional, List, Tuple, Union, Iterable

from siliconcompiler import Checklist


class ASICChecklist(Checklist):
    """A Checklist for validating ASIC flow results against a set of rules.

    This class dynamically builds a checklist by loading rules from specified
    JSON files. It filters the rules based on the target standard cell library
    and flow, expands any wildcard definitions for flow steps or indices, and
    constructs the criteria and tasks needed for verification by the
-   SiliconCompiler framework.
    """

    def __init__(self,
                 job: str,
                 flow: str,
                 mainlib: str,
                 flow_nodes: Iterable[Tuple[str, str]],
                 rules_files: Union[str, List[str], Tuple[str, ...]],
                 skip_rules: Optional[List[str]] = None):
        """Initializes and configures the ASIC flow checklist.

        Args:
            job (str): The specific job name to associate with the checklist tasks.
            flow (str): The name of the flow being checked (e.g., 'asicflow').
            mainlib (str): The main standard cell library used, which is used to
                select the correct rule set from the rules file.
            flow_nodes (Iterable[Tuple[str, str]]): An iterable of (step, index)
                tuples representing the actual nodes in the flow graph. This is
                used to expand wildcard ('*') rules.
            rules_files (Union[str, List[str], Tuple[str, ...]]): A path or list
                of paths to the JSON file(s) containing the verification rules.
            skip_rules (Optional[List[str]], optional): A list of rule names
                to exclude from the check. Supports glob-style wildcards.
                Defaults to None.

        Raises:
            ValueError: If no rules file is provided, or if the specified
                `mainlib` or `flow` is not found in the loaded rules.
        """
        super().__init__()
        self.set_name("asicflow_rules")

        if not rules_files:
            raise ValueError('no rules file provided')

        if not isinstance(rules_files, (list, tuple)):
            rules_files = [rules_files]

        # Read in and merge all specified rule files
        rules = {}
        for rules_file in rules_files:
            with open(rules_file, 'r') as f:
                rules.update(json.load(f))

        if mainlib not in rules:
            raise ValueError(f'{mainlib} is missing from rules')
        if flow not in rules[mainlib]:
            raise ValueError(f'{flow} is missing from rules')

        rules = rules[mainlib][flow]["rules"]

        # Ensure we can iterate over flow_nodes multiple times
        flow_nodes = tuple(flow_nodes)

        for name, info in rules.items():
            criteria = set()
            nodes = set()

            if skip_rules:
                skip = False
                for skip_rule in skip_rules:
                    if fnmatch.fnmatch(name, skip_rule):
                        skip = True
                if skip:
                    continue

            # Expand wildcard nodes based on the actual flow graph
            nodes = set()
            for node in info['nodes']:
                if node['step'] == '*':
                    steps = [step for step, _ in flow_nodes]
                else:
                    steps = [node['step']]

                for step in steps:
                    if node['index'] == '*':
                        indexes = [index for nstep, index in flow_nodes if step == nstep]
                    else:
                        indexes = [node['index']]

                    for index in indexes:
                        nodes.add((job, step, index))

            # Construct criteria strings
            criteria = set()
            for rule in info['criteria']:
                if rule['value'] is None:
                    continue

                criteria.add(f"{rule['metric']}{rule['operator']}{rule['value']}")

            self.set(name, 'criteria', criteria)
            self.set(name, 'task', nodes)


if __name__ == "__main__":
    # This script is not meant to be executed directly as a command-line tool.
    # The following code is for development purposes, primarily to reformat
    # the JSON template for better readability.
    try:
        with open('asicflow_template.json', 'r') as f:
            rules = json.load(f)

        with open('asicflow_template.json', 'w') as f:
            json.dump(rules, f, indent=4, sort_keys=True)
    except FileNotFoundError:
        print("asicflow_template.json not found. Skipping reformat.")
