#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery
from lambdalib import ramlib

import glob
from siliconcompiler.package import path as sc_path


def setup():
    chip = Chip('wally')

    chip.register_source('wally',
                         path='git+https://github.com/infinitymdm/cvw',
                         ref='552a212c85aab41bafa7db929d1e40bfd1ee1608')

    chip.set('option', 'entrypoint', 'wallypipelinedcorewrapper')

    config = 'rv64gc'

    # Add source files
    for src in ('src/cvw.sv',):
        chip.input(src, package='wally')

    chip.input('wally/extra/wallypipelinedcorewrapper.sv', package='scgallery-designs')

    wally_path = sc_path(chip, 'wally')
    for src in glob.glob(f'{wally_path}/src/*/*.sv'):
        chip.input(os.path.relpath(src, wally_path), package='wally')

    for src in glob.glob(f'{wally_path}/src/*/*/*.sv'):
        chip.input(os.path.relpath(src, wally_path), package='wally')

    chip.add('option', 'idir', 'config/shared', package='wally')
    chip.add('option', 'idir', f'config/{config}', package='wally')

    # chip.input(os.path.join(extra_root, 'lambda.v'), package='scgallery-designs')
    # chip.use(ramlib)

    return chip


def setup_physical(chip):
    # Disable yosys flattening to avoid massive memory requirement
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'flatten', False)
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'auto_flatten', False)


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=asap7_demo, module_path=__file__)
    setup_physical(chip)

    chip.run()
    chip.summary()
