#!/usr/bin/env python3

'''
Key vault from Calpitra-RTL

Source: https://github.com/chipsalliance/caliptra-rtl
'''

from siliconcompiler import Chip
from siliconcompiler.targets import freepdk45_demo
from scgallery.designs.caliptra.src import keyvault
from scgallery import Gallery


def setup():
    chip = Chip('caliptra-keyvault')

    chip.use(keyvault)

    chip.set('option', 'entrypoint', 'kv')

    return chip


def setup_physical(chip):
    chip.set('constraint', 'density', 20)
    chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.25')


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=freepdk45_demo)
    setup_physical(chip)

    chip.run()
    chip.summary()
