#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import freepdk45_demo
from scgallery.libraries.freepdk45.fakeram45 import fakeram45


def setup(target=freepdk45_demo,
          use_cmd_file=False):
    chip = Chip('tiny_rocket')
    chip.set('option', 'entrypoint', 'RocketTile')

    if use_cmd_file:
        chip.create_cmdline(chip.design)

    aes_root = os.path.dirname(__file__)
    src_root = os.path.join(aes_root, 'src')
    extra_root = os.path.join(aes_root, 'extra')
    sdc_root = os.path.join(aes_root, 'constraints')

    for src in ('freechips.rocketchip.system.TinyConfig.v',
                'AsyncResetReg.v',
                'ClockDivider2.v',
                'plusarg_reader.v'):
        chip.input(os.path.join(src_root, src))

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    sdc = os.path.join(sdc_root, f'{mainlib}.sdc')
    if not os.path.exists(sdc):
        raise FileNotFoundError(f'Cannot find {sdc} constraints')

    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'))

    chip.set('option', 'define', 'SYNTHESIS')

    if mainlib == 'nangate45':
        chip.use(fakeram45)
        chip.add('asic', 'macrolib', 'fakeram45_64x32')
        chip.add('asic', 'macrolib', 'fakeram45_1024x32')

        chip.set('option', 'skipcheck', True)

        chip.input(os.path.join(extra_root, f'{mainlib}.v'))

        chip.set('constraint', 'outline', [(0, 0),
                                           (924.92, 799.4)])
        chip.set('constraint', 'corearea', [(10.07, 9.8),
                                            (914.85, 789.6)])

    return chip


if __name__ == '__main__':
    chip = setup(use_cmd_file=True)

    chip.run()
    chip.summary()
