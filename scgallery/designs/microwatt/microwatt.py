#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import skywater130_demo


def setup(target=skywater130_demo,
          use_cmd_file=False):
    chip = Chip('microwatt')
    chip.set('option', 'entrypoint', 'core')

    if use_cmd_file:
        chip.create_cmdline(chip.design)

    aes_root = os.path.dirname(__file__)
    src_root = os.path.join(aes_root, 'microwatt')
    sdc_root = os.path.join(aes_root, 'constraints')

    for src in ('decode_types.vhdl', 'common.vhdl', 'wishbone_types.vhdl', 'fetch1.vhdl',
                'utils.vhdl', 'plrufn.vhdl', 'cache_ram.vhdl', 'icache.vhdl',
                'predecode.vhdl', 'decode1.vhdl', 'helpers.vhdl', 'insn_helpers.vhdl',
                'control.vhdl', 'decode2.vhdl', 'register_file.vhdl',
                'cr_file.vhdl', 'crhelpers.vhdl', 'ppc_fx_insns.vhdl', 'rotator.vhdl',
                'logical.vhdl', 'countbits.vhdl', 'multiply.vhdl', 'multiply-32s.vhdl',
                'divider.vhdl', 'execute1.vhdl', 'loadstore1.vhdl', 'mmu.vhdl', 'dcache.vhdl',
                'writeback.vhdl', 'core_debug.vhdl', 'core.vhdl', 'fpu.vhdl', 'pmu.vhdl'):
        chip.input(os.path.join(src_root, src))

    for src in ('wishbone_arbiter.vhdl', 'wishbone_bram_wrapper.vhdl', 'sync_fifo.vhdl',
                'wishbone_debug_master.vhdl', 'xics.vhdl', 'syscon.vhdl', 'gpio.vhdl', 'soc.vhdl',
                'spi_rxtx.vhdl', 'spi_flash_ctrl.vhdl'):
        chip.input(os.path.join(src_root, src))

    for src in ('dmi_dtm_dummy.vhdl', 'fpga/soc_reset.vhdl', 'fpga/pp_fifo.vhd',
                'fpga/pp_soc_uart.vhd', 'fpga/main_bram.vhdl', 'nonrandom.vhdl',
                'fpga/clk_gen_bypass.vhd', 'fpga/top-generic.vhdl'):
        chip.input(os.path.join(src_root, src))

# -gMEMORY_SIZE=$(MEMORY_SIZE) -gRAM_INIT_FILE=$(RAM_INIT_FILE) \
# 	-gRESET_LOW=$(RESET_LOW) -gCLK_INPUT=$(CLK_INPUT) -gCLK_FREQUENCY=$(CLK_FREQUENCY) \
#   -gICACHE_NUM_LINES=$(ICACHE_NUM_LINES) \
# 	$(LITEDRAM_GHDL_ARG)


# clkgen=fpga/clk_gen_bypass.vhd
# toplevel=fpga/top-generic.vhdl

    chip.set('option', 'frontend', 'vhdl')
    chip.add('option', 'define', 'MEMORY_SIZE=8192')
    chip.add('option', 'define', 'RESET_LOW=true')
    chip.add('option', 'define', 'CLK_INPUT=50000000')
    chip.add('option', 'define', 'CLK_FREQUENCY=40000000')
    chip.add('option', 'define', 'ICACHE_NUM_LINES=4')

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    sdc = os.path.join(sdc_root, f'{mainlib}.sdc')
    if os.path.exists(sdc):
        chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'))

    if mainlib.startswith('sky130'):
        # chip.use(microwatt_ip)
        # chip.add('asic', 'macrolib', 'microwatt_ip')

        chip.set('constraint', 'outline', [(0, 0),
                                           (2920, 3520)])
        chip.set('constraint', 'corearea', [(10, 10),
                                            (2910, 3510)])

        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.20')
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'autoname', 'false')

    return chip


if __name__ == '__main__':
    chip = setup(use_cmd_file=True)

    chip.run()
    chip.summary()
