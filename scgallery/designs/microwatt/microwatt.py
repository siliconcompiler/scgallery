#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import skywater130_demo
from siliconcompiler.tools.openroad import openroad
from scgallery.designs.microwatt.libraries.skywater130 import microwatt_ip


def setup(target=skywater130_demo):
    chip = Chip('microwatt')

    if __name__ == '__main__':
        chip.create_cmdline(chip.design)

    mod_root = os.path.dirname(__file__)
    src_root = os.path.join(mod_root, 'src')
    sdc_root = os.path.join(mod_root, 'constraints')

    for src in ('microwatt.v',
                'raminfr.v',
                'simplebus_host.v',
                'tap_top.v',
                'uart_defines.v',
                'uart_receiver.v',
                'uart_regs.v',
                'uart_rfifo.v',
                'uart_sync_flops.v',
                'uart_tfifo.v',
                'uart_top.v',
                'uart_transmitter.v',
                'uart_wb.v'):
        chip.input(os.path.join(src_root, src))

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'))

    for task in chip._get_tool_tasks(openroad):
        chip.set('tool', 'openroad', 'task', task, 'var', 'sta_early_timing_derate', '0.95')
        chip.set('tool', 'openroad', 'task', task, 'var', 'sta_late_timing_derate', '1.05')

    if mainlib.startswith('sky130'):
        chip.use(microwatt_ip)
        chip.add('asic', 'macrolib', ['Microwatt_FP_DFFRFile',
                                      'multiply_add_64x64',
                                      'RAM32_1RW1R',
                                      'RAM512'])

        chip.set('constraint', 'outline', [(0, 0),
                                           (2920, 3520)])
        chip.set('constraint', 'corearea', [(10, 10),
                                            (2910, 3510)])

        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.25')
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'autoname', 'false')

        chip.set('tool', 'openroad', 'task', 'place', 'var',
                 'cts_clock_buffer', 'sky130_fd_sc_hd__clkbuf_8')
        chip.set('tool', 'openroad', 'task', 'place', 'var',
                 'cts_distance_between_buffers', '600')
        chip.set('tool', 'openroad', 'task', 'place', 'var',
                 'cts_cluster_diameter', '100')
        chip.set('tool', 'openroad', 'task', 'place', 'var',
                 'cts_cluster_size', '30')

        chip.set('constraint', 'component', 'soc0.bram.bram0.ram_0.memory_0',
                 'placement', (1460.27, 2985.2, 0))
        chip.set('constraint', 'component', 'soc0.processor.dcache_0.rams:1.way.cache_ram_0',
                 'placement', (626.75, 133.52, 0))
        chip.set('constraint', 'component', 'soc0.processor.icache_0.rams:1.way.cache_ram_0',
                 'placement', (2292.87, 133.52, 0))
        chip.set('constraint', 'component', 'soc0.processor.execute1_0.multiply_0.multiplier',
                 'placement', (315.02, 802.68, 0))
        chip.set('constraint', 'component', 'soc0.processor.with_fpu.fpu_0.fpu_multiply_0.multiplier',  # noqa: E501
                 'placement', (315.02, 1917.88, 0))
        chip.set('constraint', 'component', 'soc0.processor.register_file_0.register_file_0',
                 'placement', (2304.6, 1361.08, 0))

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
