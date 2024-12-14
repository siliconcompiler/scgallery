#!/usr/bin/env python3

'''
Advanced Encryption Standard

Source: http://www.opencores.org/cores/aes_core/
'''

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery


def setup():
    chip = Chip('aes')
    chip.set('option', 'entrypoint', 'aes_cipher_top')

    src_root = os.path.join('aes', 'src')

    for src in ('aes_cipher_top.v',
                'aes_inv_cipher_top.v',
                'aes_inv_sbox.v',
                'aes_key_expand_128.v',
                'aes_rcon.v',
                'aes_sbox.v'):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    chip.add('option', 'idir', src_root, package='scgallery-designs')

    return chip


def setup_physical(chip):
    for task in ('global_placement', 'pin_placement'):
        chip.set('tool', 'openroad', 'task', task, 'var', 'place_density', '0.65')

    if chip.get('option', 'pdk') == 'skywater130':
        # Decrease density due to high routing runtime
        chip.set('constraint', 'density', 30)

        for task in ('global_placement', 'pin_placement'):
            chip.set('tool', 'openroad', 'task', task, 'var', 'place_density', '0.50')


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=asap7_demo, module_path=__file__)
    setup_physical(chip)

    chip.run()
    chip.summary()
