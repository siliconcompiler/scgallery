#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery


def setup():
    chip = Chip('ibex')
    chip.set('option', 'entrypoint', 'ibex_core')

    chip.register_source('opentitan',
                         path='git+https://github.com/lowRISC/opentitan.git',
                         ref='6074460f410bd6302cec90f32c7bb96aa8011243')
    chip.register_source('ibex',
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

    chip.input('vendor/lowrisc_ip/ip/prim/rtl/prim_cipher_pkg.sv', package='ibex')

    chip.add('option', 'idir', 'rtl', package='ibex')

    chip.add('option', 'idir', 'hw/ip/prim/rtl', package='opentitan')
    chip.add('option', 'idir', 'hw/dv/sv/dv_utils', package='opentitan')

    return chip


def setup_physical(chip):
    chip.add('option', 'define', 'SYNTHESIS')

    if chip.get('option', 'pdk') == 'asap7':
        chip.set('tool', 'openroad', 'task', 'detailed_placement', 'var', 'enable_dpo', 'false')
    elif chip.get('option', 'pdk') == 'skywater130':
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'map_adders', 'false')


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=asap7_demo, module_path=__file__)
    setup_physical(chip)

    chip.run()
    chip.summary()
