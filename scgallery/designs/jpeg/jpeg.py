#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from siliconcompiler.tools.openroad import openroad


def setup(target=asap7_demo,
          use_cmd_file=False):
    chip = Chip('jpeg')
    chip.set('option', 'entrypoint', 'jpeg_encoder')

    if use_cmd_file:
        chip.create_cmdline(chip.design)

    aes_root = os.path.dirname(__file__)
    src_root = os.path.join(aes_root, 'src')
    sdc_root = os.path.join(aes_root, 'constraints')

    chip.set('option', 'idir', os.path.join(src_root, 'include'))
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
        chip.set('constraint', 'density', 30)
        chip.set('constraint', 'aspectratio', 1)
        chip.set('constraint', 'coremargin', 2)

        for task in chip._get_tool_tasks(openroad):
            chip.set('tool', 'openroad', 'task', task, 'var',
                     'place_density', '0.60')
    elif mainlib == 'nangate45':
        chip.set('constraint', 'density', 45)
        for task in chip._get_tool_tasks(openroad):
            chip.set('tool', 'openroad', 'task', task, 'var',
                     'place_density', '0.50')
    elif mainlib.startswith('sky130'):
        chip.set('constraint', 'density', 55)
        for task in chip._get_tool_tasks(openroad):
            chip.set('tool', 'openroad', 'task', task, 'var',
                     'place_density', '0.60')

    return chip


if __name__ == '__main__':
    chip = setup(use_cmd_file=True)

    chip.run()
    chip.summary()
