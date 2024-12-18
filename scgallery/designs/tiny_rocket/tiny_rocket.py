#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import freepdk45_demo
from scgallery import Gallery
from lambdalib import ramlib


def setup():
    chip = Chip('tiny_rocket')
    chip.set('option', 'entrypoint', 'RocketTile')

    src_root = os.path.join('tiny_rocket', 'src')
    extra_root = os.path.join('tiny_rocket', 'extra')

    for src in ('freechips.rocketchip.system.TinyConfig.v',
                'AsyncResetReg.v',
                'ClockDivider2.v',
                'plusarg_reader.v'):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    chip.input(os.path.join(extra_root, 'lambda.v'), package='scgallery-designs')
    chip.use(ramlib)

    return chip


def setup_physical(chip):
    chip.set('option', 'define', 'SYNTHESIS')


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=freepdk45_demo, module_path=__file__)
    setup_physical(chip)

    chip.run()
    chip.summary()
