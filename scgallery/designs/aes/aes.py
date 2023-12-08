#!/usr/bin/env python3

'''
Advanced Encryption Standard

Source: http://www.opencores.org/cores/aes_core/
'''

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery


def setup(target=asap7_demo):
    chip = Chip('aes')
    chip.set('option', 'entrypoint', 'aes_cipher_top')

    if __name__ == '__main__':
        Gallery.design_commandline(chip)

    src_root = os.path.join('aes', 'src')
    sdc_root = os.path.join('aes', 'constraints')

    for src in ('aes_cipher_top.v',
                'aes_inv_cipher_top.v',
                'aes_inv_sbox.v',
                'aes_key_expand_128.v',
                'aes_rcon.v',
                'aes_sbox.v'):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    if mainlib.startswith('asap7sc7p5t'):
        # Setup for ASAP7 asap7sc7p5t
        chip.set('constraint', 'density', 40)
        chip.set('constraint', 'aspectratio', 1)
        chip.set('constraint', 'coremargin', 2)

        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.65')
    elif mainlib.startswith('sky130'):
        chip.set('constraint', 'density', 40)
        chip.set('constraint', 'aspectratio', 1)
        chip.set('constraint', 'coremargin', 2)

        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.65')
    elif mainlib == 'nangate45':
        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.65')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
