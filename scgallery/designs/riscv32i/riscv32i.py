#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import skywater130_demo
from scgallery import Gallery


def setup(target=skywater130_demo):
    chip = Chip('riscv32i')
    chip.set('option', 'entrypoint', 'riscv')

    if __name__ == '__main__':
        Gallery.design_commandline(chip)

    src_root = os.path.join('riscv32i', 'src')
    sdc_root = os.path.join('riscv32i', 'constraints')

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

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
