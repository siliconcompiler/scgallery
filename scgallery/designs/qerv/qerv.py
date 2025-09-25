#!/usr/bin/env python3

from scgallery import GalleryDesign
from siliconcompiler import ASICProject
from siliconcompiler.targets import asap7_demo
from scgallery.designs.serv.serv import SERVDesign
from siliconcompiler.tools.yosys.syn_asic import ASICSynthesis
from siliconcompiler.tools import get_task


class QERVDesign(GalleryDesign):
    def __init__(self):
        super().__init__("qerv")
        self.set_dataroot("extra", __file__)
        self.set_dataroot("qerv",
                          'git+https://github.com/olofk/qerv.git',
                          tag='aa129c1eebf1cf6966ee06d6e50353db7cd24623')

        with self.active_dataroot("qerv"):
            with self.active_fileset("rtl"):
                self.set_topmodule("serv_synth_wrapper")
                self.add_file([
                    'rtl/serv_synth_wrapper.v',
                    'rtl/serv_top.v',
                    'rtl/qerv_immdec.v'])
                self.add_depfileset(SERVDesign(), "rtl.serv_core")

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

    def setup_gf180(self, project: ASICProject):
        get_task(project, filter=ASICSynthesis).set("var", "use_slang", True)

    def setup_skywater130(self, project: ASICProject):
        get_task(project, filter=ASICSynthesis).set("var", "use_slang", True)


if __name__ == '__main__':
    project = ASICProject(QERVDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    asap7_demo(project)
    project.design.process_setups("asap7_asap7sc7p5t_rvt", project)

    project.run()
    project.summary()
