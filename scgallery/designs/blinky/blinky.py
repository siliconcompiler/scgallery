#!/usr/bin/env python3

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery


def setup():
    chip = Chip('blinky')

    chip.register_source(name='blinky',
                         path='git+https://github.com/fusesoc/blinky.git',
                         ref='b88a2a644723fc0c44827750fd054f09ce316b0b')

    chip.input('blinky.v', package='blinky')

    chip.set('option', 'param', 'clk_freq_hz', '1000000')

    return chip


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=asap7_demo, module_path=__file__)

    chip.run()
    chip.summary()
