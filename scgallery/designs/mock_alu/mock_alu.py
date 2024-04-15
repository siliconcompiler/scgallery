#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery


def setup(target=asap7_demo):
    chip = Chip('mock_alu')
    chip.set('option', 'entrypoint', 'MockAlu')

    chip.set('option', 'frontend', 'chisel')
    if __name__ == '__main__':
        Gallery.design_commandline(chip)

    src_root = os.path.join('mock_alu', 'src')
    sdc_root = os.path.join('mock_alu', 'constraints')

    for src in ('build.sbt',):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    chip.set('tool', 'chisel', 'task', 'convert', 'var', 'application',
             'GenerateMockAlu')
    chip.add('tool', 'chisel', 'task', 'convert', 'var', 'argument',
             '--width 64')
    operations = ['ADD',
                  'SUB',
                  'AND',
                  'OR',
                  'XOR',
                  'SHL',
                  'SHR',
                  'SRA',
                  'SETCC_EQ',
                  'SETCC_NE',
                  'SETCC_LT',
                  'SETCC_ULT',
                  'SETCC_LE',
                  'SETCC_ULE',
                  'MULT']
    chip.add('tool', 'chisel', 'task', 'convert', 'var', 'argument',
             f'--operations {",".join(operations)}')

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    chip.add('tool', 'chisel', 'task', 'convert', 'var', 'argument', '--tech none')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
