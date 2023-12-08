#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery


def setup(target=asap7_demo):
    chip = Chip('dynamic_node')
    chip.set('option', 'entrypoint', 'dynamic_node_top_wrap')

    if __name__ == '__main__':
        Gallery.design_commandline(chip)

    src_root = os.path.join('dynamic_node', 'src')
    sdc_root = os.path.join('dynamic_node', 'constraints')

    for src in ('dynamic_node.pickle.v',):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    if mainlib == 'nangate45':
        chip.set('constraint', 'density', 40)
        chip.set('constraint', 'coremargin', 5)
        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.45')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
