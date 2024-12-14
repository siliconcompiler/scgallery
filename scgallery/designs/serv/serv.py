#!/usr/bin/env python3

from siliconcompiler import Chip
from siliconcompiler.targets import skywater130_demo
from scgallery import Gallery

from scgallery.designs.serv.src import serv as serv_lib


def setup():
    chip = Chip('serv')
    chip.set('option', 'entrypoint', 'serv_top')

    chip.use(serv_lib)

    return chip


def setup_lint(chip):
    chip.set('tool', 'verilator', 'task', 'lint', 'file', 'config',
             'data/verilator_waiver.vlt', package='serv')


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=skywater130_demo, module_path=__file__)

    chip.run()
    chip.summary()
