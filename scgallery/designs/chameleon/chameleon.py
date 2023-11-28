#!/usr/bin/env python3

import os

from siliconcompiler import Chip
from siliconcompiler.targets import skywater130_demo
from scgallery.designs.chameleon.libraries.skywater130 import chameleon_ip


def setup(target=skywater130_demo):
    chip = Chip('chameleon')
    chip.set('option', 'entrypoint', 'soc_core')

    if __name__ == '__main__':
        chip.create_cmdline(chip.design)

    src_root = os.path.join('chameleon', 'src')
    sdc_root = os.path.join('chameleon', 'constraints')

    for src in ('soc_core.v',
                'AHB_sys_0/AHBlite_sys_0.v',
                'AHB_sys_0/AHBlite_bus0.v',
                'AHB_sys_0/AHBlite_db_reg.v',
                'AHB_sys_0/AHBlite_GPIO.v',
                'acc/AHB_SPM.v',
                'IPs/APB_I2C.v',
                'IPs/APB_SPI.v',
                'IPs/APB_UART.v',
                'IPs/AHBSRAM.v',
                'IPs/DFFRAMBB.v',
                'IPs/GPIO.v',
                'IPs/i2c_master.v',
                'IPs/PWM32.v',
                'IPs/QSPI_XIP_CTRL.v',
                'IPs/RAM_3Kx32.v',
                'IPs/spi_master.v',
                'IPs/TIMER32.v',
                'IPs/WDT32.v'):
        chip.input(os.path.join(src_root, src), package='scgallery-designs')

    if not chip.get('option', 'target'):
        chip.load_target(target)

    mainlib = chip.get('asic', 'logiclib')[0]
    chip.input(os.path.join(sdc_root, f'{mainlib}.sdc'), package='scgallery-designs')

    if mainlib.startswith('sky130'):
        chip.use(chameleon_ip)
        chip.add('asic', 'macrolib', ['apb_sys_0',
                                      'DFFRAM_4K',
                                      'DMC_32x16HC',
                                      'ibex_wrapper'])

        chip.set('constraint', 'outline', [(0, 0),
                                           (2920, 3520)])
        chip.set('constraint', 'corearea', [(20, 20),
                                            (2900, 3500)])

        chip.set('constraint', 'component', r'RAM.genblk1\[0\].RAM', 'placement',
                 (745, 845, 0))
        chip.set('constraint', 'component', r'RAM.genblk1\[1\].RAM', 'placement',
                 (2145, 845, 0))
        chip.set('constraint', 'component', r'RAM.genblk1\[2\].RAM', 'placement',
                 (745, 2644, 0))
        chip.set('constraint', 'component', r'RAM.genblk1\[2\].RAM', 'rotation', 180)
        chip.set('constraint', 'component', r'ahb_sys_0_uut.S0.CACHE', 'placement',
                 (2300, 2950, 0))
        chip.set('constraint', 'component', r'ibex_core', 'placement',
                 (2450, 2100, 0))
        chip.set('constraint', 'component', r'ahb_sys_0_uut.apb_sys_inst_0', 'placement',
                 (1700, 3000, 0))

    return chip


if __name__ == '__main__':
    chip = setup()

    chip.run()
    chip.summary()
