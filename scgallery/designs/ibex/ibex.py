#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery


def setup(target=asap7_demo):
    chip = Chip('ibex')
    chip.set('option', 'entrypoint', 'ibex_core')

    chip.set('option', 'frontend', 'systemverilog')
    if __name__ == '__main__':
        Gallery.design_commandline(chip)

    sdc_root = os.path.join('ibex', 'constraints')

    chip.register_package_source('opentitan',
                                 path='git+https://github.com/lowRISC/opentitan.git',
                                 ref='6074460f410bd6302cec90f32c7bb96aa8011243')
    chip.register_package_source('ibex',
                                 path='git+https://github.com/lowRISC/ibex.git',
                                 ref='d097c918f5758b11995098103fdad6253fe555e7')

    for src in ('ibex_pkg.sv',
                'ibex_alu.sv',
                'ibex_compressed_decoder.sv',
                'ibex_controller.sv',
                'ibex_counter.sv',
                'ibex_cs_registers.sv',
                'ibex_decoder.sv',
                'ibex_ex_block.sv',
                'ibex_id_stage.sv',
                'ibex_if_stage.sv',
                'ibex_load_store_unit.sv',
                'ibex_multdiv_slow.sv',
                'ibex_multdiv_fast.sv',
                'ibex_prefetch_buffer.sv',
                'ibex_fetch_fifo.sv',
                'ibex_register_file_ff.sv',
                'ibex_core.sv',
                'ibex_csr.sv',
                'ibex_wb_stage.sv',):
        chip.input(os.path.join('rtl', src), package='ibex')
    for src in ('hw/ip/prim/rtl/prim_assert.sv',):
        chip.input(src, package='opentitan')
    chip.input('hw/dv/sv/dv_utils/dv_fcov_macros.svh',
               fileset='rtl',
               filetype='verilog',
               package='opentitan')

    chip.add('option', 'define', 'SYNTHESIS')

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    if mainlib.startswith('asap7sc7p5t'):
        chip.set('tool', 'openroad', 'task', 'place', 'var', 'enable_dpo', 'false')
    elif mainlib == 'nangate45':
        pass
    elif mainlib.startswith('sky130'):
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'map_adders', 'false')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
