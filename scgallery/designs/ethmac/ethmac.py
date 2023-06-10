#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from siliconcompiler.tools.openroad import openroad


def setup(target=asap7_demo,
          use_cmd_file=False):
    chip = Chip('aes')

    if use_cmd_file:
        chip.create_cmdline(chip.design)

    aes_root = os.path.dirname(__file__)
    src_root = os.path.join(aes_root, 'src')
    sdc_root = os.path.join(aes_root, 'constraints')

    for src in ('ethmac.v',
                'ethmac_defines.v',
                'eth_clockgen.v',
                'eth_cop.v',
                'eth_crc.v',
                'eth_fifo.v',
                'eth_maccontrol.v',
                'eth_macstatus.v',
                'eth_miim.v',
                'eth_outputcontrol.v',
                'eth_random.v',
                'eth_receivecontrol.v',
                'eth_register.v',
                'eth_registers.v',
                'eth_rxaddrcheck.v',
                'eth_rxcounters.v',
                'eth_rxethmac.v',
                'eth_rxstatem.v',
                'eth_shiftreg.v',
                'eth_spram_256x32.v',
                'eth_top.v',
                'eth_transmitcontrol.v',
                'eth_txcounters.v',
                'eth_txethmac.v',
                'eth_txstatem.v',
                'eth_wishbone.v'):
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

        for task in chip._get_tool_tasks(openroad):
            chip.set('tool', 'openroad', 'task', task, 'var',
                     'place_density', '0.60')

    return chip


if __name__ == '__main__':
    chip = setup(use_cmd_file=True)

    chip.run()
    chip.summary()
