#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import skywater130_demo
from scgallery import Gallery


def setup():
    chip = Chip('openmsp430')
    chip.set('option', 'entrypoint', 'openMSP430')

    src_root = os.path.join('core', 'rtl', 'verilog')

    chip.register_source(name='openmsp430',
                         path='git+https://github.com/olgirard/openmsp430.git',
                         ref='92c883abb4518dbc35b027e6cad5ffef5b2fbb81')

    for src in ('openMSP430.v',
                'omsp_frontend.v',
                'omsp_execution_unit.v',
                'omsp_register_file.v',
                'omsp_alu.v',
                'omsp_sfr.v',
                'omsp_clock_module.v',
                'omsp_mem_backbone.v',
                'omsp_watchdog.v',
                'omsp_dbg.v',
                'omsp_dbg_uart.v',
                'omsp_dbg_i2c.v',
                'omsp_dbg_hwbrk.v',
                'omsp_multiplier.v',
                'omsp_sync_reset.v',
                'omsp_sync_cell.v',
                'omsp_scan_mux.v',
                'omsp_and_gate.v',
                'omsp_wakeup_cell.v',
                'omsp_clock_gate.v',
                'omsp_clock_mux.v'):
        chip.input(os.path.join(src_root, src), package='openmsp430')

    return chip


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=skywater130_demo, module_path=__file__)

    chip.run()
    chip.summary()
