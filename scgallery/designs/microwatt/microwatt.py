#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import skywater130_demo
from scgallery.designs.microwatt.libraries.skywater130 import microwatt_ip
from siliconcompiler.tools.builtin import nop


def setup(target=skywater130_demo,
          use_cmd_file=False):
    chip = Chip('microwatt')

    if use_cmd_file:
        chip.create_cmdline(chip.design)

    aes_root = os.path.dirname(__file__)
    src_root = os.path.join(aes_root, 'src')
    sdc_root = os.path.join(aes_root, 'constraints')

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
    sdc = os.path.join(sdc_root, f'{mainlib}.sdc')
    if not os.path.exists(sdc):
        raise FileNotFoundError(f'Cannot find {sdc} constraints')

    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'))

    # RTL contains \edge and other constructs surelog doesn't like
    chip.set('flowgraph', 'asicflow', 'import', '0', 'tool', 'builtin')
    chip.set('flowgraph', 'asicflow', 'import', '0', 'task', 'nop')
    chip.set('flowgraph', 'asicflow', 'import', '0', 'taskmodule', nop.__name__)

    if mainlib.startswith('sky130'):
        chip.use(microwatt_ip)
        chip.add('asic', 'macrolib', 'microwatt_ip')

        chip.set('constraint', 'outline', [(0, 0),
                                           (2920, 3520)])
        chip.set('constraint', 'corearea', [(10, 10),
                                            (2910, 3510)])

        chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.20')

    return chip


if __name__ == '__main__':
    chip = setup(use_cmd_file=True)

    chip.run()
    chip.summary()
