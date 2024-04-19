#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import freepdk45_demo
from scgallery.designs import _common
from scgallery import Gallery


def setup(target=freepdk45_demo):
    chip = Chip('tiny_rocket')
    chip.set('option', 'entrypoint', 'RocketTile')

    if __name__ == '__main__':
        Gallery.design_commandline(chip)

    src_root = os.path.join('tiny_rocket', 'src')
    extra_root = os.path.join('tiny_rocket', 'extra')
    sdc_root = os.path.join('tiny_rocket', 'constraints')

    for src in ('freechips.rocketchip.system.TinyConfig.v',
                'AsyncResetReg.v',
                'ClockDivider2.v',
                'plusarg_reader.v'):
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
                                           (924.92, 799.4)])
        chip.set('constraint', 'corearea', [(10.07, 9.8),
                                            (914.85, 789.6)])
    elif mainlib.startswith('asap7'):
        pass
    elif mainlib.startswith('sky130'):
        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.4')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
