#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery


def setup(target=asap7_demo):
    chip = Chip('jpeg')
    chip.set('option', 'entrypoint', 'jpeg_encoder')

    if __name__ == '__main__':
        Gallery.design_commandline(chip)

    src_root = os.path.join('jpeg', 'src')
    sdc_root = os.path.join('jpeg', 'constraints')

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

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
