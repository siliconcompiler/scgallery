#!/usr/bin/env python3

'''
Secure Hash Algorithms 512 bits from Calpitra-RTL

Source: https://github.com/chipsalliance/caliptra-rtl
'''

import os

from siliconcompiler import Chip
from siliconcompiler.targets import freepdk45_demo
from scgallery.designs.caliptra._common import (
    add_sha512,
    add_pcrvault,
    add_keyvault,
    add_libs,
    add_caliptra_top_defines
)


def setup(target=freepdk45_demo):
    chip = Chip('caliptra-sha512')

    if __name__ == '__main__':
        chip.create_cmdline(chip.design)

    sdc_root = os.path.join('caliptra', 'constraints', 'sha512')

    add_sha512(chip)
    add_pcrvault(chip)
    add_keyvault(chip)
    add_libs(chip)
    add_caliptra_top_defines(chip)

    chip.set('option', 'entrypoint', 'sha512_ctrl')
    chip.set('option', 'frontend', 'systemverilog')

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
