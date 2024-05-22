#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import skywater130_demo
from scgallery import Gallery


def setup(target=skywater130_demo):
    chip = Chip('picorv32')

    if __name__ == '__main__':
        Gallery.design_commandline(chip)

    sdc_root = os.path.join('picorv32', 'constraints')

    chip.register_package_source(name='picorv32',
                                 path='git+https://github.com/YosysHQ/picorv32.git',
                                 ref='c0acaebf0d50afc6e4d15ea9973b60f5f4d03c42')

    for src in ('picorv32.v',):
        chip.input(src, package='picorv32')

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
