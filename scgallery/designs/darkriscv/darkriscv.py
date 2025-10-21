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

from scgallery import GalleryDesign
from siliconcompiler import ASIC
from siliconcompiler.targets import asap7_demo
from siliconcompiler.tools.openroad._apr import OpenROADGPLParameter
from lambdalib.ramlib import Spram


class DarkSOCVDesign(GalleryDesign):
    def __init__(self):
        super().__init__("darksocv")

        self.set_dataroot("extra", __file__)
        self.set_dataroot("darkriscv",
                          'git+https://github.com/darklife/darkriscv.git',
                          tag='7c653744d29926499e1e562984b792099cdf25ad')

        with self.active_dataroot("darkriscv"):
            with self.active_fileset("rtl"):
                self.set_topmodule("darksocv")
                self.add_file([
                    'rtl/darksocv.v',
                    'rtl/darkriscv.v',
                    'rtl/darkuart.v',
                    'rtl/darkio.v',
                    'rtl/darkbridge.v',
                    'rtl/darkpll.v'])
                self.add_idir("rtl")
        with self.active_dataroot("extra"):
            with self.active_fileset("rtl"):
                self.add_file("extra/darkram.v")
                self.add_depfileset(Spram(), "rtl")

            with self.active_fileset("sdc.asap7sc7p5t_rvt"):
                self.add_file("constraints/asap7sc7p5t_rvt.sdc")

            with self.active_fileset("sdc.gf180mcu_fd_sc_mcu7t5v0_5LM"):
                self.add_file("constraints/gf180mcu_fd_sc_mcu7t5v0.sdc")

            with self.active_fileset("sdc.gf180mcu_fd_sc_mcu9t5v0_5LM"):
                self.add_file("constraints/gf180mcu_fd_sc_mcu9t5v0.sdc")

            with self.active_fileset("sdc.nangate45"):
                self.add_file("constraints/nangate45.sdc")

            with self.active_fileset("sdc.sg13g2_stdcell_1p2"):
                self.add_file("constraints/sg13g2_stdcell.sdc")

            with self.active_fileset("sdc.sky130hd"):
                self.add_file("constraints/sky130hd.sdc")

        self.add_target_setup("freepdk45_nangate45", self.setup_freepdk45)
        self.add_target_setup("asap7_asap7sc7p5t_rvt", self.setup_asap7)
        self.add_target_setup("ihp130_sg13g2_stdcell", self.setup_ihp130)
        self.add_target_setup("gf180_gf180mcu_fd_sc_mcu7t5v0", self.setup_gf180)
        self.add_target_setup("gf180_gf180mcu_fd_sc_mcu9t5v0", self.setup_gf180)
        self.add_target_setup("skywater130_sky130hd", self.setup_skywater130)

    def setup_freepdk45(self, project: ASIC):
        project.constraint.area.set_density(30)
        for task in OpenROADGPLParameter.find_task(project):
            task.set("var", "gpl_uniform_placement_adjustment", 0.1)

    def setup_asap7(self, project: ASIC):
        project.constraint.area.set_density(25)
        for task in OpenROADGPLParameter.find_task(project):
            task.set("var", "gpl_uniform_placement_adjustment", 0.05)

    def setup_ihp130(self, project: ASIC):
        for task in OpenROADGPLParameter.find_task(project):
            task.set("var", "gpl_uniform_placement_adjustment", 0.05)

    def setup_gf180(self, project: ASIC):
        for task in OpenROADGPLParameter.find_task(project):
            task.set("var", "gpl_uniform_placement_adjustment", 0.1)

    def setup_skywater130(self, project: ASIC):
        for task in OpenROADGPLParameter.find_task(project):
            task.set("var", "gpl_uniform_placement_adjustment", 0.1)


if __name__ == '__main__':
    project = ASIC(DarkSOCVDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    asap7_demo(project)
    project.design.process_setups("asap7_asap7sc7p5t_rvt", project)

    project.run()
    project.summary()
