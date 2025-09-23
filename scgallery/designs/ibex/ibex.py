#!/usr/bin/env python3

from scgallery import GalleryDesign
from siliconcompiler import ASICProject
from siliconcompiler.targets import asap7_demo
from siliconcompiler.tools.yosys.syn_asic import ASICSynthesis
from siliconcompiler.tools import get_task


class IBEXDesign(GalleryDesign):
    def __init__(self):
        super().__init__("ibex")
        self.set_dataroot("extra", __file__)
        self.set_dataroot("opentitan",
                          'git+https://github.com/lowRISC/opentitan.git',
                          tag='6074460f410bd6302cec90f32c7bb96aa8011243')
        self.set_dataroot("ibex",
                          'git+https://github.com/lowRISC/ibex.git',
                          tag='d097c918f5758b11995098103fdad6253fe555e7')

        with self.active_dataroot("ibex"):
            with self.active_fileset("rtl"):
                self.set_topmodule("ibex_core")
                self.add_file([
                    'rtl/ibex_pkg.sv',
                    'rtl/ibex_alu.sv',
                    'rtl/ibex_compressed_decoder.sv',
                    'rtl/ibex_controller.sv',
                    'rtl/ibex_counter.sv',
                    'rtl/ibex_cs_registers.sv',
                    'rtl/ibex_decoder.sv',
                    'rtl/ibex_ex_block.sv',
                    'rtl/ibex_id_stage.sv',
                    'rtl/ibex_if_stage.sv',
                    'rtl/ibex_load_store_unit.sv',
                    'rtl/ibex_multdiv_slow.sv',
                    'rtl/ibex_multdiv_fast.sv',
                    'rtl/ibex_prefetch_buffer.sv',
                    'rtl/ibex_fetch_fifo.sv',
                    'rtl/ibex_register_file_ff.sv',
                    'rtl/ibex_core.sv',
                    'rtl/ibex_csr.sv',
                    'rtl/ibex_wb_stage.sv'])
                self.add_define("SYNTHESIS")
                self.add_idir("rtl")

        with self.active_dataroot("opentitan"):
            with self.active_fileset("rtl"):
                self.add_idir("hw/ip/prim/rtl")
                self.add_idir("hw/dv/sv/dv_utils")

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

    def setup_asap7(self, project: ASICProject):
        get_task(project, filter=ASICSynthesis).set("var", "use_slang", True)

    def setup_ihp130(self, project: ASICProject):
        get_task(project, filter=ASICSynthesis).set("var", "use_slang", True)
        project.get_areaconstraints().set_aspectratio(0.25)

    def setup_gf180(self, project: ASICProject):
        get_task(project, filter=ASICSynthesis).set("var", "use_slang", True)

    def setup_skywater130(self, project: ASICProject):
        get_task(project, filter=ASICSynthesis).set("var", "use_slang", True)
        get_task(project, filter=ASICSynthesis).set("var", "map_adders", False)
        project.get_areaconstraints().set_aspectratio(0.80)


if __name__ == '__main__':
    project = ASICProject(IBEXDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    asap7_demo.setup(project)
    project.design.process_setups("asap7_asap7sc7p5t_rvt", project)

    project.run()
    project.summary()
