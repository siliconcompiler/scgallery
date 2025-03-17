#!/usr/bin/env python3
"""
Developed in a magic night of 19 Aug, 2018 between 2am and 8am, the DarkRISCV softcore started as
an proof of concept for the opensource RISC-V instruction set.

Although the code is small and crude when compared with other RISC-V implementations, the DarkRISCV
has lots of impressive features:

implements most of the RISC-V RV32E instruction set
implements most of the RISC-V RV32I instruction set
optional CSRs for interrupts and debug
works up to 250MHz in a ultrascale ku040 (400MHz w/ overclock!)
up to 100MHz in a cheap spartan-6, fits in small spartan-3E such as XC3S100E!
can sustain 1 clock per instruction most of time (typically 70% of time)
flexible harvard architecture (easy to integrate a cache controller, bus bridges, etc)
works fine in a real xilinx (spartan-3, spartan-6, spartan-7, artix-7, kintex-7 and kintex
ultrascale)
works fine with some real altera and lattice FPGAs
works fine with gcc 9.0.0 and above for RISC-V (no patches required!)
uses between 850-1500LUTs (core only with LUT6 technology, depending of enabled features and
optimizations)
optional RV32E support (works better with LUT4 FPGAs)
optional 16x16-bit MAC instruction (for digital signal processing)
optional coarse-grained multi-threading (MT)
no interlock between pipeline stages!
optional interrupt handled on machine level
optional breakpoints handled on supervisor level
optional instruction and data caches
optional harvard to von neumann bridge
optional SDRAM controller (from kianRiscV project)
optional support for big-endian
BSD license: can be used anywhere with no restrictions!
"""

import os

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery
from lambdalib import ramlib


def setup():
    chip = Chip('darksocv')

    extra_root = os.path.join('darkriscv', 'extra')

    chip.register_source('darkriscv',
                         path='git+https://github.com/darklife/darkriscv.git',
                         ref='7c653744d29926499e1e562984b792099cdf25ad')

    for src in ('darksocv.v',
                'darkriscv.v',
                'darkuart.v',
                'darkio.v',
                'darkbridge.v',
                'darkpll.v',):
        chip.input(os.path.join('rtl', src), package='darkriscv')

    chip.add('option', 'idir', 'rtl', package='darkriscv')

    chip.use(ramlib)
    chip.input(os.path.join(extra_root, "darkram.v"), package='scgallery-designs')

    return chip


def setup_physical(chip):
    if chip.get('option', 'pdk') == 'freepdk45':
        chip.set('constraint', 'density', 30)
        for task in ('macro_placement', 'global_placement', 'pin_placement'):
            chip.set('tool', 'openroad', 'task', task, 'var', 'gpl_uniform_placement_adjustment',
                     '0.10')
    if chip.get('option', 'pdk') == 'asap7':
        chip.set('constraint', 'density', 25)
        for task in ('macro_placement', 'global_placement', 'pin_placement'):
            chip.set('tool', 'openroad', 'task', task, 'var', 'gpl_uniform_placement_adjustment',
                     '0.05')
    if chip.get('option', 'pdk') == 'ihp130':
        for task in ('macro_placement', 'global_placement', 'pin_placement'):
            chip.set('tool', 'openroad', 'task', task, 'var', 'gpl_uniform_placement_adjustment',
                     '0.05')
    if chip.get('option', 'pdk') == 'gf180':
        for task in ('macro_placement', 'global_placement', 'pin_placement'):
            chip.set('tool', 'openroad', 'task', task, 'var', 'gpl_uniform_placement_adjustment',
                     '0.10')
    if chip.get('option', 'pdk') == 'skywater130':
        for task in ('macro_placement', 'global_placement', 'pin_placement'):
            chip.set('tool', 'openroad', 'task', task, 'var', 'gpl_uniform_placement_adjustment',
                     '0.10')


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=asap7_demo, module_path=__file__)
    setup_physical(chip)

    chip.run()
    chip.summary()
