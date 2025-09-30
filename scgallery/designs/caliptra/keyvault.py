#!/usr/bin/env python3

'''
Key vault from Calpitra-RTL

Source: https://github.com/chipsalliance/caliptra-rtl
'''

from siliconcompiler import ASIC
from siliconcompiler.targets import asap7_demo
from scgallery.designs.caliptra import KeyVault


if __name__ == '__main__':
    project = ASIC(KeyVault())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    asap7_demo(project)
    project.design.process_setups("asap7_asap7sc7p5t_rvt", project)

    project.run()
    project.summary()
