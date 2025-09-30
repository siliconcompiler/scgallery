#!/usr/bin/env python3
'''
FazyRV -- A Scalable RISC-V Core
A minimal-area RISC-V core with a scalable data path to 1, 2, 4, or 8 bits and manifold variants.
'''

from scgallery import GalleryDesign
from siliconcompiler import ASICProject
from siliconcompiler.targets import asap7_demo
from lambdalib.ramlib import Spram
from siliconcompiler.tools.openroad.macro_placement import MacroPlacementTask
from siliconcompiler.tools.yosys.syn_asic import ASICSynthesis
from siliconcompiler.tools import get_task


class FazyRVDesign(GalleryDesign):
    def __init__(self):
        super().__init__("fazyrv")
        self.set_dataroot("extra", __file__)
        self.set_dataroot("fazyrv",
                          'https://github.com/meiniKi/FazyRV/archive/',
                          tag='f287cf56b06ed20ead2d1dd0aab0c64ee50c5133')

        with self.active_dataroot("fazyrv"):
            with self.active_fileset("rtl"):
                self.set_topmodule("fsoc")
                self.add_file([
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
                    'soc/rtl/fsoc.sv'])
                self.set_param("RFTYPE", '"BRAM"')
                self.set_param("CONF", '"MIN"')
                self.set_param("CHUNKSIZE", '8')
                self.add_define("SYNTHESIS")

        with self.active_dataroot("extra"):
            with self.active_fileset("rtl"):
                self.add_file("extra/fazyrv_ram_sp.sv")
                self.add_file("extra/wb_ram.sv")
                self.add_depfileset(Spram(), "rtl")

        with self.active_dataroot("extra"):
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

    def setup_freepdk45(self, project: ASICProject):
        get_task(project, filter=ASICSynthesis).set("var", "use_slang", True)
        get_task(project, filter=MacroPlacementTask).set("var", "macro_place_halo", [10, 10])

    def setup_asap7(self, project: ASICProject):
        get_task(project, filter=ASICSynthesis).set("var", "use_slang", True)
        get_task(project, filter=MacroPlacementTask).set("var", "macro_place_halo", [5, 1])

    def setup_ihp130(self, project: ASICProject):
        get_task(project, filter=ASICSynthesis).set("var", "use_slang", True)
        get_task(project, filter=MacroPlacementTask).set("var", "macro_place_halo", [20, 35])
        project.constraint.area.set_aspectratio(0.25)

    def setup_gf180(self, project: ASICProject):
        get_task(project, filter=ASICSynthesis).set("var", "use_slang", True)

    def setup_skywater130(self, project: ASICProject):
        get_task(project, filter=ASICSynthesis).set("var", "use_slang", True)
        project.constraint.area.set_aspectratio(0.80)


if __name__ == '__main__':
    project = ASICProject(FazyRVDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    asap7_demo(project)
    project.design.process_setups("asap7_asap7sc7p5t_rvt", project)

    project.run()
    project.summary()
