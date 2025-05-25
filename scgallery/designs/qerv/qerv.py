#!/usr/bin/env python3

from siliconcompiler import Chip
from siliconcompiler.targets import skywater130_demo
from scgallery import Gallery

from scgallery.designs.serv.src import serv_reg_file


def setup():
    chip = Chip('qerv')
    chip.set('option', 'entrypoint', 'serv_synth_wrapper')

    chip.register_source(
        name='qerv',
        path='git+https://github.com/olofk/qerv.git',
        ref='aa129c1eebf1cf6966ee06d6e50353db7cd24623')

    for src in ('rtl/serv_synth_wrapper.v',
                'rtl/serv_top.v',
                'rtl/qerv_immdec.v'):
        chip.input(src, package='qerv')

    chip.use(serv_reg_file)

    return chip


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=skywater130_demo, module_path=__file__)

    chip.run()
    chip.summary()
