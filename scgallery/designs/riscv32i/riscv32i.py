#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import skywater130_demo
from scgallery import Gallery


def setup():
    chip = Chip('riscv32i')
    chip.set('option', 'entrypoint', 'riscv')

    src_root = os.path.join('riscv32i', 'src')

    for src in ('adder.v',
                'alu.v',
                'aludec.v',
                'controller.v',
                'datapath.v',
                'dmem.v',
                'flopenr.v',
                'flopens.v',
                'flopr.v',
                'magcompare2b.v',
                'magcompare2c.v',
                'magcompare32.v',
                'maindec.v',
                'mux2.v',
                'mux3.v',
                'mux4.v',
                'mux5.v',
                'mux8.v',
                'regfile.v',
                'riscv.v',
                'rom.v',
                'shifter.v',
                'signext.v',
                'top.v'):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    return chip


def setup_lint(chip):
    chip.set('tool', 'verilator', 'task', 'lint', 'file', 'config',
             'riscv32i/lint/verilator', package='scgallery-designs')


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=skywater130_demo, module_path=__file__)

    chip.run()
    chip.summary()
