#!/usr/bin/env python3

'''
Data vault from Calpitra-RTL

Source: https://github.com/chipsalliance/caliptra-rtl
'''

import os

from siliconcompiler import Chip
from siliconcompiler.targets import freepdk45_demo
from scgallery.designs.caliptra._common import add_datavault, add_libs, add_caliptra_top_defines
from scgallery import Gallery


def setup(target=freepdk45_demo):
    chip = Chip('caliptra-datavault')

    if __name__ == '__main__':
        Gallery.design_commandline(chip)

    sdc_root = os.path.join('caliptra', 'constraints', 'datavault')

    add_datavault(chip)
    add_libs(chip)
    add_caliptra_top_defines(chip)

    chip.set('option', 'entrypoint', 'dv')
    chip.set('option', 'frontend', 'systemverilog')

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    if mainlib.startswith('asap7sc7p5t'):
        chip.set('constraint', 'density', 30)
        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.40')
    elif mainlib.startswith('sky130'):
        chip.set('constraint', 'density', 30)
        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.40')
    elif mainlib.startswith('nangate45'):
        chip.set('constraint', 'density', 30)
        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.40')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
