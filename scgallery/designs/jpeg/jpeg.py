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

    if mainlib.startswith('asap7sc7p5t'):
        # Setup for ASAP7 asap7sc7p5t
        chip.set('constraint', 'density', 30)
        chip.set('constraint', 'aspectratio', 1)
        chip.set('constraint', 'coremargin', 2)

        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.60')
    elif mainlib == 'nangate45':
        chip.set('constraint', 'density', 45)
        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.50')
    elif mainlib.startswith('sky130'):
        chip.set('constraint', 'density', 55)
        chip.set('tool', 'openroad', 'task', 'place', 'var', 'gpl_uniform_placement_adjustment',
                 '0.20')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
