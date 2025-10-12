"""A command-line utility for creating, checking, and updating rule checklists.

This script provides functionality to interact with JSON-based rule files
used for verifying SiliconCompiler project results. It can:
1. Create a new rules file from a template based on a completed run.
2. Check a completed run against an existing rules file.
3. Update an existing rules file based on new run results, with various
   methods for updating (e.g., only failing rules, all rules).
"""
import argparse
import sys
import json
import math
import os.path
from typing import Union, Dict, Optional
from enum import Enum, auto
from datetime import datetime
from scgallery.checklists import asicflow_rules
from siliconcompiler import utils, ASIC
from siliconcompiler.flowgraph import RuntimeFlowgraph


class UpdateMethod(Enum):
    """Enumeration for different methods of updating rule values."""
    All = auto()
    OnlyFailing = auto()
    TightenPassing = auto()


def new_value(project: ASIC,
              metric: str, job: str,
              step: str, index: str,
              operator: str,
              padding: Optional[float],
              margin: Optional[Union[float, int]],
              bounds: Optional[Dict[str, Union[float, int]]]) -> Optional[Union[int, float]]:
    """Calculates a new rule value based on a metric from a completed run.

    This function fetches a metric value from a specified job history and
    applies padding, margin, and bounds to compute a new potential value for a rule.

    Args:
        project (ASIC): The SiliconCompiler project object.
        metric (str): The name of the metric to query.
        job (str): The job name from which to pull the history.
        step (str): The flow step of the metric.
        index (str): The index of the metric.
        operator (str): The comparison operator (e.g., '<=', '>=') for the rule.
        padding (Optional[float]): A relative padding to apply (e.g., 0.1 for 10%).
        margin (Optional[Union[float, int]]): An absolute margin to apply.
        bounds (Optional[Dict[str, Union[float, int]]]): A dictionary with 'min'
            and/or 'max' keys to constrain the new value.

    Returns:
        Optional[Union[int, float]]: The calculated new value, or None if the
        base metric could not be found.
    """
    jobproject = project.history(job)
    value: Union[None, float, int] = jobproject.get('metric', metric, step=step, index=index)

    if value is None:
        return None

    if operator == '==':
        return value

    sc_type: str = jobproject.get('metric', metric, field='type')

    newvalue = value
    if padding:
        if '>' in operator:
            newvalue *= 1 - (padding if newvalue >= 0 else -padding)
        elif '<' in operator:
            newvalue *= 1 + (padding if newvalue >= 0 else -padding)
    elif margin:
        if '>' in operator:
            newvalue -= margin
        elif '<' in operator:
            newvalue += margin

    if sc_type == 'int':
        if '>' in operator:
            newvalue = math.floor(newvalue)
        elif '<' in operator:
            newvalue = math.ceil(newvalue)
        newvalue = int(newvalue)

    if bounds:
        if 'max' in bounds:
            newvalue = min(bounds['max'], newvalue)
        if 'min' in bounds:
            newvalue = max(bounds['min'], newvalue)

    return newvalue


def update_rule_value(project: ASIC, metric: str,
                      job: str,
                      step: str, index: str,
                      operator: str,
                      check_value: Union[float, int],
                      padding: Optional[float],
                      margin: Optional[Union[float, int]],
                      bounds: Optional[Dict[str, Union[float, int]]],
                      method: UpdateMethod) -> Optional[Union[float, int]]:
    """Determines the updated value for a rule based on the update method.

    This function compares the current metric value against the existing rule's
    check value. Based on the specified update method, it decides whether to
    keep the old value or compute a new one.

    Args:
        project (ASIC): The SiliconCompiler project object.
        metric (str): The name of the metric.
        job (str): The job name.
        step (str): The flow step.
        index (str): The metric index.
        operator (str): The rule's comparison operator.
        check_value (Union[float, int]): The current value in the rule being checked.
        padding (Optional[float]): Relative padding for new value calculation.
        margin (Optional[Union[float, int]]): Absolute margin for new value calculation.
        bounds (Optional[Dict[str, Union[float, int]]]): Bounds for new value.
        method (UpdateMethod): The update strategy to use.

    Returns:
        Optional[Union[float, int]]: The new value for the rule, which may be
        the same as the original `check_value` if no update is needed. Returns
        None if the metric cannot be found.
    """
    jobproject = project.history(job)
    value: Union[float, int] = jobproject.get('metric', metric, step=step, index=index)

    if value is None:
        return None

    is_passing = utils.safecompare(value, operator, check_value)
    if method == UpdateMethod.OnlyFailing and is_passing:
        return check_value

    new_check_value = new_value(project,
                                metric,
                                job, step, index,
                                operator,
                                padding,
                                margin,
                                bounds)

    if new_check_value is None or new_check_value == check_value:
        return check_value

    if method == UpdateMethod.TightenPassing and \
       not utils.safecompare(new_check_value, operator, check_value):
        return check_value

    return new_check_value


def create_rules(project: ASIC) -> Dict:
    """Creates a new set of rules from a template for a given project run.

    This function loads a template JSON file, iterates through the defined rules,
    and populates the initial 'value' for each criterion based on the metrics
    from the completed project run.

    Args:
        project (ASIC): The project object after a run has completed.

    Returns:
        Dict: A dictionary containing the newly generated rules.
    """
    template = os.path.join(os.path.dirname(__file__), 'checklists', 'asicflow_template.json')
    with open(template) as f:
        new_rules: Dict = json.load(f)

    job = project.option.get_jobname()

    for info in new_rules.values():
        nodes = set((node['step'], node['index']) for node in info['nodes'])
        used_nodes = set()

        for criteria in info['criteria']:
            if len(nodes) > 1:
                used_nodes = nodes
                continue

            for step, index in nodes:
                if step == '*' or index == '*':
                    used_nodes.add((step, index))
                    continue

                try:
                    value = new_value(
                        project,
                        criteria['metric'],
                        job, step, index,
                        criteria['operator'],
                        criteria['update']['padding'],
                        criteria['update']['margin'],
                        criteria['update']['bounds'])
                except (ValueError, KeyError):
                    continue

                criteria['value'] = value
                used_nodes.add((step, index))

        info['nodes'] = [{"step": step, "index": index} for step, index in used_nodes]

    # Clean up rules that have no valid nodes
    for rule in list(new_rules.keys()):
        if not new_rules[rule]['nodes']:
            del new_rules[rule]

    return new_rules


def update_rules(project: ASIC, method: UpdateMethod, rules: Dict) -> None:
    """Updates an existing dictionary of rules based on a project run.

    This function iterates through a provided set of rules and updates the
    'value' of each criterion based on the metrics from the completed project
    run and the specified update method.

    Args:
        project (ASIC): The project object after a run has completed.
        method (UpdateMethod): The strategy to use for updating rule values.
        rules (Dict): The dictionary of rules to be updated in-place.

    Raises:
        ValueError: If the project's mainlib or flow is not found in the rules.
    """
    mainlib = project.get("asic", "mainlib")
    if mainlib not in rules:
        raise ValueError(f'{mainlib} is missing from rules')

    flow = project.option.get_flow()
    if flow not in rules[mainlib]:
        raise ValueError(f'{flow} is missing from rules for {mainlib}')

    rules[mainlib][flow]["date"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    for rule, info in rules[mainlib][flow]['rules'].items():
        nodes = set((node['step'], node['index']) for node in info['nodes'])
        if len(nodes) > 1:
            continue

        for criteria in info['criteria']:
            for step, index in nodes:
                if step == '*' or index == '*':
                    continue

                try:
                    value = update_rule_value(
                        project,
                        criteria['metric'],
                        project.option.get_jobname(), step, index,
                        criteria['operator'],
                        criteria['value'],
                        criteria['update']['padding'],
                        criteria['update']['margin'],
                        criteria['update']['bounds'],
                        method)
                except (ValueError, KeyError):
                    continue

                if criteria['value'] != value:
                    criteria_prefix = f"{criteria['metric']}{criteria['operator']}"
                    project.logger.info(
                        f"Updating {rule} for {project.option.get_jobname()}/{step}/{index} from "
                        f"{criteria_prefix}{criteria['value']} to {criteria_prefix}{value}")
                    criteria['value'] = value


if __name__ == "__main__":
    # --- Command-line interface setup ---
    parser = argparse.ArgumentParser(
        'sc-rules',
        description='A utility for creating, checking, and updating SiliconCompiler rule files.'
    )
    parser.add_argument('-cfg',
                        required=True,
                        metavar='<file>',
                        help='Path to the manifest file of a completed run.')
    parser.add_argument('-rules',
                        required=True,
                        metavar='<file>',
                        help='Path to the JSON rules file to check or update.')

    mode_parser = parser.add_mutually_exclusive_group(required=True)
    mode_parser.add_argument('-check',
                             action='store_true',
                             help='Check the run against the rules file.')
    mode_parser.add_argument('-create',
                             action='store_true',
                             help='Create a new rules entry from a template.')
    mode_parser.add_argument('-update_all',
                             action='store_true',
                             help='Update all rule values based on the run.')
    mode_parser.add_argument('-tighten_passing',
                             action='store_true',
                             help='Update rule values only if they are passing and become stricter.')
    mode_parser.add_argument('-update_failing',
                             action='store_true',
                             help='Update rule values only for failing checks.')

    args = parser.parse_args()

    if not os.path.exists(args.cfg):
        raise FileNotFoundError(f"Manifest file not found: {args.cfg}")

    project: ASIC = ASIC.from_manifest(args.cfg)
    mainlib: str = project.get('asic', 'mainlib')

    rules = {}
    if args.create:
        if os.path.exists(args.rules):
            with open(args.rules, 'r') as f:
                rules = json.load(f)
        if mainlib in rules:
            raise ValueError(f"'{mainlib}' already exists in the rules file. Cannot create.")

        rules[mainlib] = {
            project.option.get_flow(): {
                "date": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                "rules": create_rules(project)
            }
        }
    else:
        if not os.path.exists(args.rules):
            raise FileNotFoundError(f"Rules file not found: {args.rules}")
        with open(args.rules, 'r') as f:
            rules = json.load(f)

        if args.check:
            runtime = RuntimeFlowgraph(
                project.get("flowgraph", project.option.get_flow(), field='schema'),
                from_steps=project.option.get_from(),
                to_steps=project.option.get_to(),
                prune_nodes=project.option.get_prune())
            project.summary()
            checklist = asicflow_rules.ASICChecklist(
                job=project.option.get_jobname(),
                flow=project.option.get_flow(),
                mainlib=mainlib,
                flow_nodes=runtime.get_nodes(),
                rules_files=args.rules)
            project.add_dep(checklist)
            if not checklist.check(require_reports=False):
                sys.exit(1)
            else:
                sys.exit(0)

        update_method = None
        if args.update_all:
            update_method = UpdateMethod.All
        elif args.tighten_passing:
            update_method = UpdateMethod.TightenPassing
        elif args.update_failing:
            update_method = UpdateMethod.OnlyFailing

        if update_method:
            update_rules(project, update_method, rules)

    # Write out the new or modified rules
    with open(args.rules, 'w') as f:
        json.dump(rules, f, indent=4, sort_keys=True)
