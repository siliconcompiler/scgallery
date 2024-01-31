#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery


def setup(target=asap7_demo):
    chip = Chip('swerv')

    if __name__ == '__main__':
        Gallery.design_commandline(chip)

    src_root = os.path.join('swerv', 'src')
    sdc_root = os.path.join('swerv', 'constraints')

    for src in ('swerv_wrapper.sv2v.v',):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    if mainlib == 'nangate45':
        chip.set('constraint', 'outline', [(0, 0),
                                           (1100, 1000)])
        chip.set('constraint', 'corearea', [(10, 10),
                                            (1090, 990)])

        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.45')
    elif mainlib.startswith('asap7sc7p5t'):
        chip.set('constraint', 'density', 40)

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
