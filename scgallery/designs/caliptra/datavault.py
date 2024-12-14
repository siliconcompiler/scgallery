#!/usr/bin/env python3

'''
Data vault from Calpitra-RTL

Source: https://github.com/chipsalliance/caliptra-rtl
'''

from siliconcompiler import Chip
from siliconcompiler.targets import freepdk45_demo
from scgallery.designs.caliptra.src import datavault
from scgallery import Gallery


def setup():
    chip = Chip('caliptra-datavault')

    chip.use(datavault)

    chip.set('option', 'entrypoint', 'dv')

    chip.set(*Gallery.SDC_KEY, 'caliptra/constraints/datavault', package='scgallery-designs')

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
