#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from siliconcompiler.tools._common.asic import get_mainlib
from scgallery import Gallery


def setup(target=asap7_demo):
    chip = Chip('spi')

    if __name__ == '__main__':
        Gallery.design_commandline(chip)
    else:
        chip.use(target)

    src_root = os.path.join('spi', 'src')
    sdc_root = os.path.join('spi', 'constraints')

    for src in ('spi.v',):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    mainlib = get_mainlib(chip)
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
