#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery.libraries.asap7 import fakeram, fakeregfile


def setup(target=asap7_demo):
    chip = Chip('megaboom')
    chip.set('option', 'entrypoint', 'MegaBoom')

    if __name__ == '__main__':
        chip.create_cmdline(chip.design)

    mod_root = os.path.dirname(__file__)
    src_root = os.path.join(mod_root, 'src')
    sdc_root = os.path.join(mod_root, 'constraints')

    chip.set('option', 'idir', src_root)
    for src in ('rocketchip.MegaBoomConfig.v.gz',
                'rocketchip.MegaBoomConfig.behav_srams.v'):
        chip.input(os.path.join(src_root, src))

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'))

    chip.set('tool', 'surelog', 'task', 'parse', 'var', 'enable_lowmem', 'true')

    if mainlib.startswith('asap7sc7p5t'):
        chip.use(fakeram)
        chip.use(fakeregfile)

        chip.add('asic', 'macrolib', 'fakeram_256x128')
        chip.add('asic', 'macrolib', 'fakeram_256x64')
        chip.add('asic', 'macrolib', 'fakeram_32x46')
        chip.add('asic', 'macrolib', 'fakeram_512x8')
        chip.add('asic', 'macrolib', 'fakeram_64x20')
        chip.add('asic', 'macrolib', 'fakeram_64x22')
        chip.add('asic', 'macrolib', 'fakeregfile_32x46')
        chip.add('asic', 'macrolib', 'fakeregfile_64x64')
        chip.add('asic', 'macrolib', 'fakeregfile_128x64')

        chip.set('constraint', 'outline', [(0, 0),
                                           (1400, 1400)])
        chip.set('constraint', 'corearea', [(2.538, 2.700),
                                            (1397.466, 1397.250)])

        chip.set('tool', 'openroad', 'task', 'place', 'var', 'gpl_uniform_placement_adjustment',
                 '0.05')

        chip.set('tool', 'openroad', 'task', 'floorplan', 'file', 'ppl_constraints',
                 os.path.join(mod_root, 'io.tcl'))
        chip.set('tool', 'openroad', 'task', 'place', 'file', 'ppl_constraints',
                 os.path.join(mod_root, 'io.tcl'))

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
