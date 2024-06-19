#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import skywater130_demo
from scgallery import Gallery
from siliconcompiler import package as sc_package
from scgallery.designs import _common


_top_module = 'soc'


def register_microwatt(chip):
    chip.register_package_source(
        'microwatt',
        'git+https://github.com/antonblanchard/microwatt',
        'd7458d5bebe19d20a6231471b6e0a7823365c2a6')


def setup(target=skywater130_demo):
    chip = Chip('microwatt')
    chip.set('option', 'entrypoint', _top_module)
    chip.set('option', 'frontend', 'vhdl')

    register_microwatt(chip)

    sdc_root = os.path.join('microwatt', 'constraints')
    extra_root = os.path.join('microwatt', 'extra')

    for src in ('decode_types.vhdl',
                'common.vhdl',
                'wishbone_types.vhdl',
                'fetch1.vhdl',
                'utils.vhdl',
                'plru.vhdl',
                'cache_ram.vhdl',
                'icache.vhdl',
                'decode1.vhdl',
                'helpers.vhdl',
                'insn_helpers.vhdl',
                'control.vhdl',
                'decode2.vhdl',
                'register_file.vhdl',
                'cr_file.vhdl',
                'crhelpers.vhdl',
                'ppc_fx_insns.vhdl',
                'rotator.vhdl',
                'logical.vhdl',
                'countzero.vhdl',
                'multiply.vhdl',
                'divider.vhdl',
                'execute1.vhdl',
                'loadstore1.vhdl',
                'mmu.vhdl',
                'dcache.vhdl',
                'writeback.vhdl',
                'core_debug.vhdl',
                'core.vhdl',
                'fpu.vhdl',
                'wishbone_arbiter.vhdl',
                'wishbone_bram_wrapper.vhdl',
                'sync_fifo.vhdl',
                'wishbone_debug_master.vhdl',
                'xics.vhdl',
                'syscon.vhdl',
                'gpio.vhdl',
                'soc.vhdl',
                'spi_rxtx.vhdl',
                'spi_flash_ctrl.vhdl',
                'fpga/soc_reset.vhdl',
                'fpga/pp_fifo.vhd',
                'fpga/pp_soc_uart.vhd',
                'fpga/main_bram.vhdl',
                'nonrandom.vhdl',
                'fpga/clk_gen_ecp5.vhd',
                'fpga/top-generic.vhdl',
                'dmi_dtm_dummy.vhdl'):
        chip.input(src, package='microwatt')

    for src in ('uart16550/uart_top.v',
                'uart16550/uart_regs.v',
                'uart16550/uart_wb.v',
                'uart16550/uart_transmitter.v',
                'uart16550/uart_sync_flops.v',
                'uart16550/uart_receiver.v',
                'uart16550/uart_tfifo.v',
                'uart16550/uart_rfifo.v',
                'uart16550/raminfr.v'):
        chip.input(src, package='microwatt')

    if __name__ == '__main__':
        Gallery.design_commandline(chip)

    chip.add('option', 'define', 'LOG_LENGTH=0')
    chip.add('option', 'define', 'RAM_INIT_FILE=' + sc_package.path(chip, 'microwatt') + '/hello_world/hello_world.hex')

    if not chip.get('option', 'target'):
        chip.load_target(target)

    _common.add_lambdalib_memory(chip)
    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    chip.set('constraint', 'density', 30)

    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'autoname', 'false')
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'flatten', 'false')
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'abc_clock_derating', '0.95')
    chip.set('tool', 'openroad', 'task', 'floorplan', 'var', 'rtlmp_enable', 'true')

    pdk = chip.get('option', 'pdk')
    if pdk == 'skywater130':
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'file', 'memory_libmap',
                 os.path.join(extra_root, pdk, 'memory_map.txt'), package='scgallery-designs')
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'file', 'memory_techmap',
                 os.path.join(extra_root, pdk, 'memory_techmap.v'), package='scgallery-designs')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
