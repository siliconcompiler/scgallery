#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo


def setup(target=asap7_demo,
          use_cmdline=False):
    chip = Chip('uart')

    if use_cmdline:
        chip.create_cmdline(chip.design)

    aes_root = os.path.dirname(__file__)
    src_root = os.path.join(aes_root, 'src')
    sdc_root = os.path.join(aes_root, 'constraints')

    for src in ('uart.v',
                'uart_tx.v',
                'uart_rx.v'):
        chip.input(os.path.join(src_root, src))

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    sdc = os.path.join(sdc_root, f'{mainlib}.sdc')
    if os.path.exists(sdc):
        chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'))

    if mainlib.startswith('asap7sc7p5t'):
        # Setup for ASAP7 asap7sc7p5t
        chip.set('constraint', 'outline', [(0, 0),
                                           (17, 17)])
        chip.set('constraint', 'corearea', [(1, 1),
                                            (16, 16)])

        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.70')

    return chip


if __name__ == '__main__':
    chip = setup(use_cmdline=True)

    chip.run()
    chip.summary()
