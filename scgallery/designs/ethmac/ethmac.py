#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery
from lambdalib import ramlib


def setup():
    chip = Chip('ethmac')

    src_root = os.path.join('ethmac', 'src')

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

    chip.add('option', 'idir', src_root, package='scgallery-designs')

    chip.add('option', 'define', 'ETH_VIRTUAL_SILICON_RAM')
    chip.input(os.path.join('ethmac', 'extra', 'lambda.v'), package='scgallery-designs')
    chip.use(ramlib)

    return chip


def setup_lint(chip):
    chip.set('tool', 'slang', 'task', 'lint', 'option', '--timescale 1ns/1ns')


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=asap7_demo, module_path=__file__)

    chip.run()
    chip.summary()
