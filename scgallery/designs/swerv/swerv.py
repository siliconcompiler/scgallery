#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo


def setup(target=asap7_demo,
          use_cmd_file=False):
    chip = Chip('swerv')

    if use_cmd_file:
        chip.create_cmdline(chip.design)

    aes_root = os.path.dirname(__file__)
    src_root = os.path.join(aes_root, 'src')
    extra_root = os.path.join(aes_root, 'extra')
    sdc_root = os.path.join(aes_root, 'constraints')

    for src in ('swerv_wrapper.sv2v.v',):
        chip.input(os.path.join(src_root, src))

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    sdc = os.path.join(sdc_root, f'{mainlib}.sdc')
    if os.path.exists(sdc):
        chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'))

    if mainlib == 'nangate45':
        chip.input(os.path.join(extra_root, f'{mainlib}.v'))

        chip.set('constraint', 'outline', [(0, 0),
                                           (1100, 1000)])
        chip.set('constraint', 'corearea', [(10, 10),
                                            (1090, 990)])

        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.45')

    return chip


if __name__ == '__main__':
    chip = setup(use_cmd_file=True)

    chip.run()
    chip.summary()
