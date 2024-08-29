#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import freepdk45_demo
from siliconcompiler.tools._common.asic import get_mainlib
from scgallery import Gallery
from lambdalib import ramlib


def setup(target=freepdk45_demo):
    chip = Chip('tiny_rocket')
    chip.set('option', 'entrypoint', 'RocketTile')

    if __name__ == '__main__':
        Gallery.design_commandline(chip)
    else:
        chip.use(target)

    src_root = os.path.join('tiny_rocket', 'src')
    extra_root = os.path.join('tiny_rocket', 'extra')
    sdc_root = os.path.join('tiny_rocket', 'constraints')

    for src in ('freechips.rocketchip.system.TinyConfig.v',
                'AsyncResetReg.v',
                'ClockDivider2.v',
                'plusarg_reader.v'):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    mainlib = get_mainlib(chip)
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    chip.set('option', 'define', 'SYNTHESIS')

    chip.input(os.path.join(extra_root, 'lambda.v'), package='scgallery-designs')
    chip.use(ramlib)

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
