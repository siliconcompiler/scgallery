#!/usr/bin/env python3

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery


def setup():
    chip = Chip('mock_alu')
    chip.set('option', 'entrypoint', 'MockAlu')

    chip.input('mock_alu/src/build.sbt', package='scgallery-designs')

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

    chip.add('tool', 'chisel', 'task', 'convert', 'var', 'argument', '--tech none')

    return chip


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=asap7_demo, module_path=__file__)

    chip.run()
    chip.summary()
