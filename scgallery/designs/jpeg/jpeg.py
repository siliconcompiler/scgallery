#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery


def setup():
    chip = Chip('jpeg')
    chip.set('option', 'entrypoint', 'jpeg_encoder')

    src_root = os.path.join('jpeg', 'src')

    chip.set('option', 'idir', os.path.join(src_root, 'include'), package='scgallery-designs')
    for src in ('jpeg_encoder.v',
                'jpeg_qnr.v',
                'jpeg_rle.v',
                'jpeg_rle1.v',
                'jpeg_rzs.v',
                'dct.v',
                'dct_mac.v',
                'dctu.v',
                'dctub.v',
                'div_su.v',
                'div_uu.v',
                'fdct.v',
                'zigzag.v'):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    return chip


def setup_lint(chip):
    chip.set('tool', 'verilator', 'task', 'lint', 'file', 'config',
             'jpeg/lint/verilator', package='scgallery-designs')


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=asap7_demo, module_path=__file__)

    chip.run()
    chip.summary()
