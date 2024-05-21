#!/usr/bin/env python3

'''
Source: https://github.com/black-parrot/black-parrot
'''

import os

from siliconcompiler import Chip
from siliconcompiler.targets import freepdk45_demo
from scgallery.designs import _common
from scgallery import Gallery


def setup(target=freepdk45_demo):
    chip = Chip('black_parrot')

    if __name__ == '__main__':
        Gallery.design_commandline(chip)

    src_root = os.path.join('black_parrot', 'src')
    extra_root = os.path.join('black_parrot', 'extra')
    sdc_root = os.path.join('black_parrot', 'constraints')

    for src in ('pickled.v',):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    chip.set('option', 'define', 'SYNTHESIS')

    _common.add_lambdalib_memory(chip)
    chip.input(os.path.join(extra_root, 'lambda.v'), package='scgallery-designs')

    if mainlib.startswith('sky130'):
        pass
    else:
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'strategy', 'AREA3')

    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'flatten', 'false')
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'abc_clock_derating', '0.95')

    chip.set('tool', 'openroad', 'task', 'floorplan', 'var', 'rtlmp_enable', 'true')
    chip.set('tool', 'openroad', 'task', 'floorplan', 'var', 'rtlmp_min_instances', '5000')
    chip.set('tool', 'openroad', 'task', 'floorplan', 'var', 'rtlmp_max_instances', '30000')
    chip.set('tool', 'openroad', 'task', 'floorplan', 'var', 'rtlmp_min_macros', '12')
    chip.set('tool', 'openroad', 'task', 'floorplan', 'var', 'rtlmp_max_macros', '4')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
