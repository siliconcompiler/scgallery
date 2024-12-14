#!/usr/bin/env python3

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery


def setup():
    chip = Chip('gcd')

    chip.input('gcd/src/gcd.v', package='scgallery-designs')

    return chip


def setup_physical(chip):
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'strategy', 'AREA3')
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'map_adders', 'false')


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=asap7_demo, module_path=__file__)
    setup_physical(chip)

    chip.run()
    chip.summary()
