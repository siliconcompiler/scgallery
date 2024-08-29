#!/usr/bin/env python3

'''
Ariane core

Source: https://github.com/pulp-platform/ariane
'''

import os

from siliconcompiler import Chip
from siliconcompiler.targets import freepdk45_demo
from siliconcompiler.tools._common.asic import get_mainlib
from scgallery import Gallery
from lambdalib import ramlib


def setup(target=freepdk45_demo):
    chip = Chip('ariane')

    if __name__ == '__main__':
        Gallery.design_commandline(chip)
    else:
        chip.use(target)

    src_root = os.path.join('ariane', 'src')
    sdc_root = os.path.join('ariane', 'constraints')

    for src in ('ariane.sv2v.v', 'macros.v'):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    mainlib = get_mainlib(chip)
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'flatten', 'false')
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'preserve_modules', [
             'SyncSpRamBeNx64_00000008_00000100_0_2',
             'ariane_regfile_64_2_00000002_1',
             'btb_NR_ENTRIES64',
             'csr_regfile_0000000000000000_1',
             'ex_stage',
             'fifo_v2_DEPTH8',
             'fifo_v3_0_00000020_00000008',
             'frontend_0000000000000000',
             'issue_read_operands',
             'issue_stage_NR_ENTRIES8_NR_WB_PORTS4',
             'load_store_unit',
             'miss_handler_NR_PORTS3',
             'mmu_16_16_00000001',
             'mult',
             'multiplier',
             'perf_counters',
             'scoreboard_00000008_00000004',
             'sram_00000080_00000100',
             'std_cache_subsystem_0000000080000000',
             'std_icache',
             'std_nbdcache_0000000080000000',
             'store_buffer',
             'store_unit',
             'tlb_00000010_00000001'])

    chip.set('tool', 'openroad', 'task', 'floorplan', 'var', 'rtlmp_enable', 'true')

    chip.use(ramlib)

    if mainlib.startswith('asap7sc7p5t'):
        chip.set('tool', 'openroad', 'task', 'place', 'var', 'gpl_uniform_placement_adjustment',
                 '0.05')
        chip.set('tool', 'openroad', 'task', 'route', 'var', 'M2_adjustment', '0.7')
        chip.set('tool', 'openroad', 'task', 'route', 'var', 'M3_adjustment', '0.6')

    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'abc_clock_derating', '0.95')

    chip.set('tool', 'openroad', 'task', 'floorplan', 'var',
             'rtlmp_min_instances',
             '5000')
    chip.set('tool', 'openroad', 'task', 'floorplan', 'var',
             'rtlmp_max_instances',
             '30000')
    chip.set('tool', 'openroad', 'task', 'floorplan', 'var',
             'rtlmp_min_macros',
             '16')
    chip.set('tool', 'openroad', 'task', 'floorplan', 'var',
             'rtlmp_max_macros',
             '4')

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
