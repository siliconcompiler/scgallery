#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo


def setup(target=asap7_demo,
          use_cmd_file=False,
          additional_setup=None):
    chip = Chip('gcd')

    if use_cmd_file:
        chip.create_cmdline(chip.design)

    aes_root = os.path.dirname(__file__)
    src_root = os.path.join(aes_root, 'src')
    sdc_root = os.path.join(aes_root, 'constraints')

    for src in ('gcd.v',):
        chip.input(os.path.join(src_root, src))

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    sdc = os.path.join(sdc_root, f'{mainlib}.sdc')
    if os.path.exists(sdc):
        chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'))

    if mainlib == 'nangate45':
        chip.set('constraint', 'density', 55)
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'strategy', 'AREA3')
        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.60')
    elif mainlib.startswith('sky130'):
        chip.set('constraint', 'density', 40)
        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.95')
    elif mainlib.startswith('asap7sc7p5t'):
        chip.set('constraint', 'outline', [(0, 0),
                                           (16.2, 16.2)])
        chip.set('constraint', 'corearea', [(1.08, 1.08),
                                            (15.12, 15.12)])
        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.35')

    if additional_setup:
        for setup_func in additional_setup:
            setup_func(chip)

    return chip


if __name__ == '__main__':
    chip = setup(use_cmd_file=True)

    chip.run()
    chip.summary()
