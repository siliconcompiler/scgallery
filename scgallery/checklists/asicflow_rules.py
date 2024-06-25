from siliconcompiler import Checklist
import json
import fnmatch


def setup(chip, rules_files=None, skip_rules=None):
    '''
    '''

    if not rules_files:
        raise ValueError('no rules file provided')

    if not isinstance(rules_files, (list, tuple)):
        rules_files = [rules_files]

    standard = 'asicflow_rules'

    job = chip.get('option', 'jobname')
    flow = chip.get('option', 'flow')

    checklist = Checklist(chip, standard)

    # read in all rules
    rules = {}
    for rules_file in rules_files:
        with open(rules_file, 'r') as f:
            rules.update(json.load(f))

    mainlib = chip.get('asic', 'logiclib', step='global', index='global')[0]

    if mainlib not in rules:
        raise ValueError(f'{mainlib} is missing from rules')

    flow = chip.get('option', 'flow')
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
                steps = chip.getkeys('flowgraph', flow)
            else:
                steps = [node['step']]

            for step in steps:
                if node['index'] == '*':
                    indexes = chip.getkeys('flowgraph', flow, step)
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
