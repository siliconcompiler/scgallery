#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo


def setup(target=asap7_demo):
    chip = Chip('mock_alu')
    chip.set('option', 'entrypoint', 'MockAlu')

    if __name__ == '__main__':
        chip.create_cmdline(chip.design)

    src_root = os.path.join('mock_alu', 'src')
    sdc_root = os.path.join('mock_alu', 'constraints')

    for src in ('build.sbt',):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    chip.set('option', 'frontend', 'chisel')
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

    if mainlib.startswith('asap7sc7p5t'):
        chip.add('tool', 'chisel', 'task', 'convert', 'var', 'argument',
                 f'--tech {mainlib}')

        chip.set('constraint', 'density', 50)
        chip.set('constraint', 'aspectratio', 1)
        chip.set('constraint', 'coremargin', 2)
        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.75')
    else:
        chip.add('tool', 'chisel', 'task', 'convert', 'var', 'argument',
                 '--tech none')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
