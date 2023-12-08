#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery


def setup(target=asap7_demo):
    chip = Chip('gcd')

    if __name__ == '__main__':
        Gallery.design_commandline(chip)

    src_root = os.path.join('gcd', 'src')
    sdc_root = os.path.join('gcd', 'constraints')

    for src in ('gcd.v',):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    if mainlib == 'nangate45':
        chip.set('constraint', 'density', 55)
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'strategy', 'AREA3')
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'map_adders', 'false')
        chip.set('tool', 'openroad', 'task', 'place', 'var', 'gpl_uniform_placement_adjustment',
                 '0.2')
    elif mainlib.startswith('sky130'):
        chip.set('constraint', 'density', 40)
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'map_adders', 'false')
    elif mainlib.startswith('asap7sc7p5t'):
        chip.set('constraint', 'outline', [(0, 0),
                                           (16.2, 16.2)])
        chip.set('constraint', 'corearea', [(1.08, 1.08),
                                            (15.12, 15.12)])
        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.35')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
