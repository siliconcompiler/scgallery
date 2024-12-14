#!/usr/bin/env python3

from siliconcompiler import Chip
from siliconcompiler.targets import skywater130_demo
from scgallery import Gallery


def setup():
    chip = Chip('picorv32')

    chip.register_source(name='picorv32',
                         path='git+https://github.com/YosysHQ/picorv32.git',
                         ref='c0acaebf0d50afc6e4d15ea9973b60f5f4d03c42')

    chip.input('picorv32.v', package='picorv32')

    return chip


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=skywater130_demo, module_path=__file__)

    chip.run()
    chip.summary()
