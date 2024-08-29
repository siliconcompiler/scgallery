#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from siliconcompiler.tools._common.asic import get_mainlib
from scgallery import Gallery


def setup(target=asap7_demo):
    chip = Chip('dynamic_node')
    chip.set('option', 'entrypoint', 'dynamic_node_top_wrap')

    if __name__ == '__main__':
        Gallery.design_commandline(chip)
    else:
        chip.use(target)

    sdc_root = os.path.join('dynamic_node', 'constraints')

    chip.register_source('OPDB',
                         path='git+https://github.com/PrincetonUniversity/OPDB.git',
                         ref='a80e536ba29779faed68e32d4a202f6b7a93bc9b')

    chip.input('modules/dynamic_node_2dmesh/NETWORK_2dmesh/dynamic_node_2dmesh.pickle.v',
               package='OPDB')

    mainlib = get_mainlib(chip)
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
