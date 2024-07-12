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
    lint_root = os.path.join('uart', 'lint')

    for src in ('uart.v',
                'uart_tx.v',
                'uart_rx.v'):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    # Lint setup
    chip.set('tool', 'verilator', 'task', 'lint', 'file', 'config',
             os.path.join(lint_root, 'verilator'), package='scgallery-designs')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
