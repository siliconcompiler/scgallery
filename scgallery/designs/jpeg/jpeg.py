#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from siliconcompiler.tools._common.asic import get_mainlib
from scgallery import Gallery


def setup(target=asap7_demo):
    chip = Chip('jpeg')
    chip.set('option', 'entrypoint', 'jpeg_encoder')

    if __name__ == '__main__':
        Gallery.design_commandline(chip)
    else:
        chip.use(target)

    src_root = os.path.join('jpeg', 'src')
    sdc_root = os.path.join('jpeg', 'constraints')
    lint_root = os.path.join('jpeg', 'lint')

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

    mainlib = get_mainlib(chip)
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    # Lint setup
    chip.set('tool', 'verilator', 'task', 'lint', 'file', 'config',
             os.path.join(lint_root, 'verilator'), package='scgallery-designs')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
