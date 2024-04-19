#!/usr/bin/env python3

import argparse
import os
from scgallery.designs import root


def _find_sources(source):
    sources = []

    designs_root = root()
    for dir_root, _, files in os.walk(designs_root):
        if f'{source}.sdc' in files:
            sources.append(os.path.join(dir_root, f'{source}.sdc'))

    return sources


def __process_file(source, target, subs, output_dir):
    print(f'Processing {source}')
    with open(source, 'r') as f_in:
        dir_root = os.path.relpath(os.path.dirname(source), root())
        design_path = os.path.join(output_dir, dir_root)
        os.makedirs(design_path, exist_ok=True)
        with open(os.path.join(design_path, f'{target}.sdc'), 'w') as f_out:
            for line in f_in:
                for sub_in, sub_out in subs:
                    line = _process_text(line, sub_in, sub_out)
                f_out.write(line)


def _process_text(source, sub_in, sub_out):
    if sub_in in source:
        return source.replace(sub_in, sub_out)

    return source


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        __file__,
        description='Copies a previous SDC to '
                    'a new library and replace text based '
                    'on the provided substitutions')

    parser.add_argument('--source', type=str, help='Source main library', required=True)
    parser.add_argument('--target', type=str, help='Target main library', required=True)
    parser.add_argument('--output_dir', type=str, default=root(),
                        help='Output designs directory')

    parser.add_argument(
        '--sub', type=str, nargs='+',
        default=[],
        help='Text replacements in the form of source:target')

    args = parser.parse_args()

    subs = []
    for sub in args.sub:
        subs.append(sub.split(":"))

    for src in _find_sources(args.source):
        __process_file(src, args.target, subs, args.output_dir)
