#!/usr/bin/env python3

import json
import os

jobs_file = os.path.join(os.path.dirname(__file__),
                         '..',
                         '.github',
                         'workflows',
                         'config',
                         'designs.json')


def report_skipped():
    with open(jobs_file) as fid:
        data = json.load(fid)

    data = [d for d in data if 'skip' in d and d['skip']]

    cached = [d for d in data if d['cache']]
    uncached = [d for d in data if not d['cache']]

    len_designs = max(len(d['design']) for d in data)
    len_targets = max(len(d['target']) for d in data)

    print("Cached designs")
    for setup in cached:
        design = setup['design']
        target = setup['target']
        skip = setup['skip']
        print(f'{design:>{len_designs}}: {target:>{len_targets}}: {skip}')

    print()
    print("Failing designs")
    for setup in uncached:
        design = setup['design']
        target = setup['target']
        skip = setup['skip']
        print(f'{design:>{len_designs}}: {target:>{len_targets}}: {skip}')


if __name__ == "__main__":
    report_skipped()
