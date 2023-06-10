#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo


def setup(target=asap7_demo):
    chip = Chip('heartbeat')

    if __name__ == '__main__':
        chip.create_cmdline(chip.design)

    mod_root = os.path.dirname(__file__)
    src_root = os.path.join(mod_root, 'src')
    sdc_root = os.path.join(mod_root, 'constraints')

    for src in ('heartbeat.v',):
        chip.input(os.path.join(src_root, src))

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'))

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
