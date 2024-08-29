from siliconcompiler import Checklist
import json
import fnmatch


def setup(job=None, flow=None, mainlib=None, flow_nodes=None, rules_files=None, skip_rules=None):
    '''
    '''

    if not rules_files:
        raise ValueError('no rules file provided')

    if not isinstance(rules_files, (list, tuple)):
        rules_files = [rules_files]

    standard = 'asicflow_rules'

    if not job:
        raise ValueError('job is required')

    if not flow:
        raise ValueError('flow is required')

    if not mainlib:
        raise ValueError('mainlib is required')

    if flow_nodes is None:
        raise ValueError('flow_nodes is required')

    checklist = Checklist(standard)

    # read in all rules
    rules = {}
    for rules_file in rules_files:
        with open(rules_file, 'r') as f:
            rules.update(json.load(f))

    if mainlib not in rules:
        raise ValueError(f'{mainlib} is missing from rules')

    if flow not in rules[mainlib]:
        raise ValueError(f'{flow} is missing from rules')

    rules = rules[mainlib][flow]["rules"]

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

        for node in info['nodes']:
            if node['step'] == '*':
                steps = [step for step, _ in flow_nodes]
            else:
                steps = [node['step']]

            for step in steps:
                if node['index'] == '*':
                    steps = [index for nstep, index in flow_nodes if step == nstep]
                else:
                    indexes = [node['index']]

                for index in indexes:
                    nodes.add((job, step, index))

        for rule in info['criteria']:
            if rule['value'] is None:
                continue

            criteria.add(f"{rule['metric']}{rule['operator']}{rule['value']}")

        checklist.set('checklist', standard, name, 'criteria', criteria)
        checklist.add('checklist', standard, name, 'task', nodes)

    return checklist


##################################################
if __name__ == "__main__":
    with open('asicflow_template.json', 'r') as f:
        rules = json.load(f)

    with open('asicflow_template.json', 'w') as f:
        json.dump(rules, f, indent=4, sort_keys=True)
