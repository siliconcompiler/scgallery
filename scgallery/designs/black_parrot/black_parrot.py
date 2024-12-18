#!/usr/bin/env python3

'''
Source: https://github.com/black-parrot/black-parrot
'''

import os

from siliconcompiler import Chip
from siliconcompiler.targets import freepdk45_demo
from scgallery import Gallery
from lambdalib import ramlib


def setup():
    chip = Chip('black_parrot')

    src_root = os.path.join('black_parrot', 'src')
    extra_root = os.path.join('black_parrot', 'extra')

    for src in ('pickled.v',):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    chip.input(os.path.join(extra_root, 'lambda.v'), package='scgallery-designs')
    chip.use(ramlib)

    return chip


def setup_physical(chip):
    chip.set('option', 'define', 'SYNTHESIS')

    if chip.get('option', 'pdk') == 'skywater130':
        pass
    else:
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'strategy', 'AREA3')

    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'flatten', 'false')
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'abc_clock_derating', '0.95')


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=freepdk45_demo, module_path=__file__)
    setup_physical(chip)

    chip.run()
    chip.summary()
