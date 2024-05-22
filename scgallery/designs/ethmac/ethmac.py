#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery.designs import _common
from scgallery import Gallery


def setup(target=asap7_demo):
    chip = Chip('ethmac')

    if __name__ == '__main__':
        Gallery.design_commandline(chip)

    src_root = os.path.join('ethmac', 'src')
    sdc_root = os.path.join('ethmac', 'constraints')

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
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    if not chip.get('option', 'target'):
        chip.load_target(target)

    _common.add_lambdalib_memory(chip)
    chip.add('option', 'define', 'ETH_VIRTUAL_SILICON_RAM')
    chip.input(os.path.join('ethmac', 'extra', 'lambda.v'), package='scgallery-designs')

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    chip.set('tool', 'openroad', 'task', 'floorplan', 'var', 'rtlmp_enable', 'true')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
