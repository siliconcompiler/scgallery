#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery
from lambdalib import ramlib

import glob
from siliconcompiler.package import path as sc_path
from siliconcompiler.tools import openroad
from siliconcompiler.tools._common import get_tool_tasks


def setup():
    chip = Chip('wally')

    chip.register_source('wally',
                         path='git+https://github.com/openhwgroup/cvw',
                         ref='e0af0e68a32edd8eb98abc31c8b2b7b04fbd29b9')

    chip.set('option', 'entrypoint', 'wallypipelinedcorewrapper')

    # Add source files
    chip.input('src/cvw.sv', package='wally')
    chip.input('wally/extra/wallypipelinedcorewrapper.sv', package='scgallery-designs')

    wally_path = sc_path(chip, 'wally')
    for src in glob.glob(f'{wally_path}/src/*/*.sv'):
        chip.input(os.path.relpath(src, wally_path), package='wally')

    for src in glob.glob(f'{wally_path}/src/*/*/*.sv'):
        if not ('ram' in src and 'wbe_' in src):  # Exclude hardcoded SRAMs
            chip.input(os.path.relpath(src, wally_path), package='wally')

    chip.add('option', 'idir', 'config/shared', package='wally')
    chip.add('option', 'idir', 'wally/extra/config', package='scgallery-designs')

    chip.input('wally/extra/lambda.v', package='scgallery-designs')
    chip.use(ramlib)

    return chip


def setup_physical(chip):
    # Disable yosys flattening to avoid massive memory requirement
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'use_slang', True)
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'flatten', False)
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'auto_flatten', False)
    chip.set('tool', 'openroad', 'task', 'init_floorplan', 'var', 'remove_dead_logic', False)

    chip.set('tool', 'sv2v', 'task', 'convert', 'var', 'skip_convert', True)

    for task in get_tool_tasks(chip, openroad):
        chip.set('tool', 'openroad', 'task', task, 'var', 'sta_define_path_groups', False)

    if chip.get('option', 'pdk') == 'asap7':
        chip.set('constraint', 'density', 30)


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=asap7_demo, module_path=__file__)
    setup_physical(chip)

    chip.run()
    chip.summary()
