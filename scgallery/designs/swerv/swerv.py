#!/usr/bin/env python3

from scgallery import GalleryDesign
from siliconcompiler import ASICProject
from siliconcompiler.targets import asap7_demo
from siliconcompiler.tools.yosys.syn_asic import ASICSynthesis


class SwervDesign(GalleryDesign):
    def __init__(self):
        super().__init__("swerv")

        self.set_dataroot("swerv", __file__)
        self.set_dataroot("swerv-eh1",
                          'git+https://github.com/chipsalliance/Cores-VeeR-EH1.git',
                          tag='695883a674c4a59cf96fae874ff4bfac5fecf4e8')

        with self.active_dataroot("swerv"):
            with self.active_fileset("rtl"):
                self.set_topmodule("swerv")
                self.add_file("config/common_defines.vh", filetype="systemverilog")
                self.add_idir("config")

        with self.active_dataroot("swerv-eh1"):
            with self.active_fileset("rtl"):
                self.add_file([
                    'design/include/swerv_types.sv',
                    'design/lib/beh_lib.sv',
                    'design/mem.sv',
                    'design/pic_ctrl.sv',
                    'design/dma_ctrl.sv',
                    'design/ifu/ifu_aln_ctl.sv',
                    'design/ifu/ifu_compress_ctl.sv',
                    'design/ifu/ifu_ifc_ctl.sv',
                    'design/ifu/ifu_bp_ctl.sv',
                    'design/ifu/ifu_ic_mem.sv',
                    'design/ifu/ifu_mem_ctl.sv',
                    'design/ifu/ifu_iccm_mem.sv',
                    'design/ifu/ifu.sv',
                    'design/dec/dec_decode_ctl.sv',
                    'design/dec/dec_gpr_ctl.sv',
                    'design/dec/dec_ib_ctl.sv',
                    'design/dec/dec_tlu_ctl.sv',
                    'design/dec/dec_trigger.sv',
                    'design/dec/dec.sv',
                    'design/exu/exu_alu_ctl.sv',
                    'design/exu/exu_mul_ctl.sv',
                    'design/exu/exu_div_ctl.sv',
                    'design/exu/exu.sv',
                    'design/lsu/lsu.sv',
                    'design/lsu/lsu_bus_buffer.sv',
                    'design/lsu/lsu_clkdomain.sv',
                    'design/lsu/lsu_addrcheck.sv',
                    'design/lsu/lsu_lsc_ctl.sv',
                    'design/lsu/lsu_stbuf.sv',
                    'design/lsu/lsu_bus_intf.sv',
                    'design/lsu/lsu_ecc.sv',
                    'design/lsu/lsu_dccm_mem.sv',
                    'design/lsu/lsu_dccm_ctl.sv',
                    'design/lsu/lsu_trigger.sv',
                    'design/dbg/dbg.sv',
                    'design/dmi/dmi_wrapper.v',
                    'design/dmi/dmi_jtag_to_core_sync.v',
                    'design/dmi/rvjtag_tap.sv',
                    'design/lib/mem_lib.sv',
                    'design/lib/ahb_to_axi4.sv',
                    'design/lib/axi4_to_ahb.sv',
                    'design/swerv.sv',
                    'design/swerv_wrapper.sv'])
                self.add_idir("design")
                self.add_idir("design/include")
                self.add_define('PHYSICAL')

        with self.active_dataroot("swerv"):
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
        project.get_task(filter=ASICSynthesis).set("var", "use_slang", True)

    def setup_asap7(self, project: ASICProject):
        project.get_task(filter=ASICSynthesis).set("var", "use_slang", True)

    def setup_ihp130(self, project: ASICProject):
        project.get_task(filter=ASICSynthesis).set("var", "use_slang", True)

    def setup_gf180(self, project: ASICProject):
        project.get_task(filter=ASICSynthesis).set("var", "use_slang", True)

    def setup_skywater130(self, project: ASICProject):
        project.get_task(filter=ASICSynthesis).set("var", "use_slang", True)


if __name__ == '__main__':
    project = ASICProject(SwervDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    project.load_target(asap7_demo.setup)
    project.design.process_setups("asap7_asap7sc7p5t_rvt", project)

    project.run()
    project.summary()
