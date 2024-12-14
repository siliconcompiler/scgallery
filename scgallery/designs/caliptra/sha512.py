#!/usr/bin/env python3

'''
Secure Hash Algorithms 512 bits from Calpitra-RTL

Source: https://github.com/chipsalliance/caliptra-rtl
'''

from siliconcompiler import Chip
from siliconcompiler.targets import freepdk45_demo
from scgallery.designs.caliptra.src import sha512
from scgallery import Gallery


def setup():
    chip = Chip('caliptra-sha512')

    chip.use(sha512)

    chip.set('option', 'entrypoint', 'sha512_ctrl')

    chip.set(*Gallery.SDC_KEY, 'caliptra/constraints/sha512', package='scgallery-designs')

    return chip


def setup_physical(chip):
    chip.set('constraint', 'density', 30)
    for task in ('global_placement', 'pin_placement'):
        chip.set('tool', 'openroad', 'task', task, 'var', 'place_density', '0.40')


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=freepdk45_demo, module_path=__file__)
    setup_physical(chip)

    chip.run()
    chip.summary()
