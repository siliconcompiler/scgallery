#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery


def setup(target=asap7_demo):
    chip = Chip('ibex')
    chip.set('option', 'entrypoint', 'ibex_core')

    if __name__ == '__main__':
        Gallery.design_commandline(chip)

    src_root = os.path.join('ibex', 'src')
    sdc_root = os.path.join('ibex', 'constraints')

    for src in ('ibex_alu.v',
                'ibex_branch_predict.v',
                'ibex_compressed_decoder.v',
                'ibex_controller.v',
                'ibex_core.v',
                'ibex_counter.v',
                'ibex_cs_registers.v',
                'ibex_csr.v',
                'ibex_decoder.v',
                'ibex_dummy_instr.v',
                'ibex_ex_block.v',
                'ibex_fetch_fifo.v',
                'ibex_icache.v',
                'ibex_id_stage.v',
                'ibex_if_stage.v',
                'ibex_load_store_unit.v',
                'ibex_multdiv_fast.v',
                'ibex_multdiv_slow.v',
                'ibex_pmp.v',
                'ibex_prefetch_buffer.v',
                'ibex_register_file_ff.v',
                'ibex_register_file_fpga.v',
                'ibex_register_file_latch.v',
                'ibex_wb_stage.v',
                'prim_badbit_ram_1p.v',
                'prim_clock_gating.v',
                'prim_generic_clock_gating.v',
                'prim_generic_ram_1p.v',
                'prim_lfsr.v',
                'prim_ram_1p.v',
                'prim_secded_28_22_dec.v',
                'prim_secded_28_22_enc.v',
                'prim_secded_39_32_dec.v',
                'prim_secded_39_32_enc.v',
                'prim_secded_72_64_dec.v',
                'prim_secded_72_64_enc.v',
                'prim_xilinx_clock_gating.v'):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    if mainlib.startswith('asap7sc7p5t'):
        chip.set('constraint', 'density', 40)
        chip.set('tool', 'openroad', 'task', 'place', 'var', 'enable_dpo', 'false')
    elif mainlib == 'nangate45':
        chip.set('constraint', 'density', 50)
        chip.set('tool', 'openroad', 'task', 'place', 'var', 'gpl_uniform_placement_adjustment',
                 '0.2')
    elif mainlib.startswith('sky130'):
        chip.set('constraint', 'density', 45)

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
