#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery


def setup(target=asap7_demo):
    chip = Chip('uart')

    if __name__ == '__main__':
        Gallery.design_commandline(chip)

    src_root = os.path.join('uart', 'src')
    sdc_root = os.path.join('uart', 'constraints')

    for src in ('uart.v',
                'uart_tx.v',
                'uart_rx.v'):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    if mainlib.startswith('asap7sc7p5t'):
        # Setup for ASAP7 asap7sc7p5t
        chip.set('constraint', 'outline', [(0, 0),
                                           (17, 17)])
        chip.set('constraint', 'corearea', [(1, 1),
                                            (16, 16)])

        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.70')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
