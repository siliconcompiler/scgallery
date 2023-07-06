#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import freepdk45_demo
from scgallery.libraries.freepdk45.fakeram45 import fakeram45


def setup(target=freepdk45_demo,
          use_cmdline=False):
    chip = Chip('black_parrot')

    if use_cmdline:
        chip.create_cmdline(chip.design)

    aes_root = os.path.dirname(__file__)
    src_root = os.path.join(aes_root, 'src')
    extra_root = os.path.join(aes_root, 'extra')
    sdc_root = os.path.join(aes_root, 'constraints')

    for src in ('pickled.v',):
        chip.input(os.path.join(src_root, src))

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    sdc = os.path.join(sdc_root, f'{mainlib}.sdc')
    if os.path.exists(sdc):
        chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'))

    chip.set('option', 'define', 'SYNTHESIS')

    if mainlib == 'nangate45':
        chip.use(fakeram45)
        chip.add('asic', 'macrolib', 'fakeram45_256x95')
        chip.add('asic', 'macrolib', 'fakeram45_512x64')
        chip.add('asic', 'macrolib', 'fakeram45_64x15')
        chip.add('asic', 'macrolib', 'fakeram45_64x7')
        chip.add('asic', 'macrolib', 'fakeram45_64x96')

        chip.set('option', 'skipcheck', True)

        chip.input(os.path.join(extra_root, f'{mainlib}.v'))

        chip.set('constraint', 'outline', [(0, 0),
                                           (1350, 1300)])
        chip.set('constraint', 'corearea', [(10.07, 11.2),
                                            (1340, 1290)])

        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'strategy', 'AREA3')

    return chip


if __name__ == '__main__':
    chip = setup(use_cmdline=True)

    chip.run()
    chip.summary()
