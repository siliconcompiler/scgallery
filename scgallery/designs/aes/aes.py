#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo


def setup(target=asap7_demo,
          use_cmd_file=False):
    chip = Chip('aes')
    chip.set('option', 'entrypoint', 'aes_cipher_top')

    if use_cmd_file:
        chip.create_cmdline(chip.design)

    aes_root = os.path.dirname(__file__)
    src_root = os.path.join(aes_root, 'src')
    sdc_root = os.path.join(aes_root, 'constraints')

    for src in ('aes_cipher_top.v',
                'aes_inv_cipher_top.v',
                'aes_inv_sbox.v',
                'aes_key_expand_128.v',
                'aes_rcon.v',
                'aes_sbox.v'):
        chip.input(os.path.join(src_root, src))

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    sdc = os.path.join(sdc_root, f'{mainlib}.sdc')
    if not os.path.exists(sdc):
        raise FileNotFoundError(f'Cannot find {sdc} constraints')

    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'))

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
    chip = setup(use_cmd_file=True)

    chip.run()
    chip.summary()
