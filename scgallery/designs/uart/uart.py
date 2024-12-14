#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery


def setup():
    chip = Chip('uart')

    src_root = os.path.join('uart', 'src')

    for src in ('uart.v',
                'uart_tx.v',
                'uart_rx.v'):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    return chip


def setup_lint(chip):
    chip.set('tool', 'verilator', 'task', 'lint', 'file', 'config',
             'uart/lint/verilator', package='scgallery-designs')


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=asap7_demo, module_path=__file__)

    chip.run()
    chip.summary()
