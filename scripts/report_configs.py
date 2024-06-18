#!/usr/bin/env python3

import json
import os
import argparse

jobs_file = os.path.join(os.path.dirname(__file__),
                         '..',
                         '.github',
                         'workflows',
                         'config',
                         'designs.json')


def print_table(markdown, data):
    if not data:
        print('No designs')
        return

    len_designs = max(len(d['design']) for d in data)
    len_targets = max(len(d['target']) for d in data)

    if markdown:
        print("| Design | Target | Reason |")
        print("| --- | --- | --- |")

    for setup in data:
        design = setup['design']
        target = setup['target']
        skip = setup['skip']
        if markdown:
            print(f'| {design} | {target} | {skip} |')
        else:
            print(f'{design:>{len_designs}}: {target:>{len_targets}}: {skip}')


def print_header(markdown, title):
    print(title)
    if markdown:
        print("".join(len(title) * "-"))


def report_skipped(markdown):
    with open(jobs_file) as fid:
        data = json.load(fid)

    data = [d for d in data if 'skip' in d and d['skip']]

    cached = [d for d in data if d['cache']]
    uncached = [d for d in data if not d['cache']]

    print_header(markdown, "Cached designs")
    print_table(markdown, cached)

    print()
    print_header(markdown, "Failing designs")
    print_table(markdown, uncached)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Helper script to report failing and cached designs.')
    parser.add_argument('--markdown',
                        action="store_true",
                        help="Output as markdown")

    args = parser.parse_args()

    report_skipped(args.markdown)
