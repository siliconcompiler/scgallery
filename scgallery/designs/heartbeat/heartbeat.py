#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from siliconcompiler.tools.openroad import openroad


def setup(target=asap7_demo,
          use_cmd_file=False):
    chip = Chip('heartbeat')

    if use_cmd_file:
        chip.create_cmdline(chip.design)

    aes_root = os.path.dirname(__file__)
    src_root = os.path.join(aes_root, 'src')
    sdc_root = os.path.join(aes_root, 'constraints')

    for src in ('heartbeat.v',):
        chip.input(os.path.join(src_root, src))

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    sdc = os.path.join(sdc_root, f'{mainlib}.sdc')
    if not os.path.exists(sdc):
        raise FileNotFoundError(f'Cannot find {sdc} constraints')

    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'))

    return chip


if __name__ == '__main__':
    chip = setup(use_cmd_file=True)

    chip.run()
    chip.summary()