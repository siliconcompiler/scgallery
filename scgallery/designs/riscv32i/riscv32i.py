#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import skywater130_demo


def setup(target=skywater130_demo,
          use_cmd_file=False):
    chip = Chip('riscv32i')
    chip.set('option', 'entrypoint', 'riscv')

    if use_cmd_file:
        chip.create_cmdline(chip.design)

    aes_root = os.path.dirname(__file__)
    src_root = os.path.join(aes_root, 'src')
    sdc_root = os.path.join(aes_root, 'constraints')

    for src in ('adder.v',
                'alu.v',
                'aludec.v',
                'controller.v',
                'datapath.v',
                'dmem.v',
                'flopenr.v',
                'flopens.v',
                'flopr.v',
                'magcompare2b.v',
                'magcompare2c.v',
                'magcompare32.v',
                'maindec.v',
                'mux2.v',
                'mux3.v',
                'mux4.v',
                'mux5.v',
                'mux8.v',
                'regfile.v',
                'riscv.v',
                'rom.v',
                'shifter.v',
                'signext.v',
                'top.v'):
        chip.input(os.path.join(src_root, src))

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    sdc = os.path.join(sdc_root, f'{mainlib}.sdc')
    if os.path.exists(sdc):
        chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'))

    if mainlib.startswith('sky130'):
        chip.set('constraint', 'density', 45)
        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.99')
    elif mainlib.startswith('asap7sc7p5t'):
        chip.set('constraint', 'outline', [(0, 0),
                                           (80, 80)])
        chip.set('constraint', 'corearea', [(5, 5),
                                            (75, 75)])

        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.50')

    return chip


if __name__ == '__main__':
    chip = setup(use_cmd_file=True)

    chip.run()
    chip.summary()
