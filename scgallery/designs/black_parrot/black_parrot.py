#!/usr/bin/env python3

'''
Source: https://github.com/black-parrot/black-parrot
'''

import os

from siliconcompiler import Chip
from siliconcompiler.targets import freepdk45_demo
from siliconcompiler.tools.openroad import openroad
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

    if mainlib == 'nangate45':
        chip.set('constraint', 'outline', [(0, 0),
                                           (1350, 1300)])
        chip.set('constraint', 'corearea', [(10.07, 11.2),
                                            (1340, 1290)])

        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'flatten', 'false')
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'strategy', 'AREA3')

        for task in chip._get_tool_tasks(openroad):
            chip.set('tool', 'openroad', 'task', task, 'var', 'gpl_uniform_placement_adjustment',
                     '0.05')
            chip.set('tool', 'openroad', 'task', task, 'var', 'ppl_arguments',
                     ['-exclude', 'left:*',
                      '-exclude', 'right:*',
                      '-exclude', 'top:*',
                      '-exclude', 'bottom:0-100',
                      '-exclude', 'bottom:1200-1350'])

        chip.set('tool', 'openroad', 'task', 'floorplan', 'var', 'macro_place_halo',
                 ['10', '10'])
        chip.set('tool', 'openroad', 'task', 'floorplan', 'var', 'macro_place_channel',
                 ['20', '20'])
    elif mainlib.startswith('asap7sc7p5t'):
        chip.set('constraint', 'density', 40)
    elif mainlib.startswith('sky130'):
        chip.set('constraint', 'density', 40)

    chip.set('tool', 'openroad', 'task', 'floorplan', 'var', 'rtlmp_enable', 'true')
    chip.set('tool', 'openroad', 'task', 'floorplan', 'var', 'rtlmp_min_instances', '5000')
    chip.set('tool', 'openroad', 'task', 'floorplan', 'var', 'rtlmp_max_instances', '30000')
    chip.set('tool', 'openroad', 'task', 'floorplan', 'var', 'rtlmp_min_macros', '12')
    chip.set('tool', 'openroad', 'task', 'floorplan', 'var', 'rtlmp_max_macros', '4')

    chip.set('tool', 'openroad', 'task', 'floorplan', 'var', 'psm_enable', 'false')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
