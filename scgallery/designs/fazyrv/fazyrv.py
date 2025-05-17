#!/usr/bin/env python3
'''
FazyRV -- A Scalable RISC-V Core
A minimal-area RISC-V core with a scalable data path to 1, 2, 4, or 8 bits and manifold variants.
'''

from siliconcompiler import Chip
from siliconcompiler.targets import skywater130_demo
from scgallery import Gallery
from lambdalib import ramlib


def setup():
    chip = Chip('fazyrv')

    chip.register_source(name='fazyrv',
                         path='git+https://github.com/meiniKi/FazyRV.git',
                         ref='f287cf56b06ed20ead2d1dd0aab0c64ee50c5133')

    chip.set('option', 'entrypoint', 'fsoc')

    chip.set('option', 'param', 'RFTYPE', '"BRAM"')
    chip.set('option', 'param', 'CONF', '"MIN"')
    chip.set('option', 'param', 'CHUNKSIZE', '8')

    for src in (
            'rtl/fazyrv_hadd.v',
            'rtl/fazyrv_fadd.v',
            'rtl/fazyrv_cmp.v',
            'rtl/fazyrv_alu.sv',
            'rtl/fazyrv_decode.sv',
            'rtl/fazyrv_decode_mem1.sv',
            'rtl/fazyrv_shftreg.sv',
            'rtl/fazyrv_csr.sv',
            'rtl/fazyrv_rf_lut.sv',
            'rtl/fazyrv_rf.sv',
            'rtl/fazyrv_pc.sv',
            'rtl/fazyrv_cntrl.sv',
            'rtl/fazyrv_spm_a.sv',
            'rtl/fazyrv_spm_d.sv',
            'rtl/fazyrv_core.sv',
            'rtl/fazyrv_top.sv',
            'soc/rtl/gpio.sv',
            'soc/rtl/fsoc.sv'):
        chip.input(src, package='fazyrv')

    chip.input('fazyrv/extra/fazyrv_ram_sp.sv', package='scgallery-designs')
    chip.input('fazyrv/extra/wb_ram.sv', package='scgallery-designs')
    chip.use(ramlib)

    return chip


def setup_physical(chip):
    chip.set('option', 'define', 'SYNTHESIS')

    if chip.get('option', 'pdk') == 'asap7':
        chip.set('tool', 'openroad', 'task', 'macro_placement', 'var', 'macro_place_halo',
                 [5, 1])
    if chip.get('option', 'pdk') == 'freepdk45':
        chip.set('tool', 'openroad', 'task', 'macro_placement', 'var', 'macro_place_halo',
                 [10, 10])
    if chip.get('option', 'pdk') == 'ihp130':
        chip.set('constraint', 'aspectratio', 0.25)
        chip.set('tool', 'openroad', 'task', 'macro_placement', 'var', 'macro_place_halo',
                 [10, 40])
    if chip.get('option', 'pdk') == 'skywater130':
        chip.set('constraint', 'aspectratio', 0.80)


def setup_lint(chip):
    chip.set('tool', 'verilator', 'task', 'lint', 'file', 'config',
             'fazyrv/lint/verilator', package='scgallery-designs')


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=skywater130_demo, module_path=__file__)

    chip.run()
    chip.summary()
