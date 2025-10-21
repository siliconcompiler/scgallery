#!/usr/bin/env python3

'''
Source: https://github.com/black-parrot/black-parrot
'''

from scgallery import GalleryDesign
from siliconcompiler import ASIC
from siliconcompiler.targets import asap7_demo
from siliconcompiler.tools.yosys.syn_asic import ASICSynthesis
from lambdalib.ramlib import Spram


class BlackParrotDesign(GalleryDesign):
    def __init__(self):
        super().__init__("black_parrot")

        self.set_dataroot("black_parrot", __file__)

        with self.active_dataroot("black_parrot"):
            with self.active_fileset("rtl"):
                self.set_topmodule("black_parrot")
                self.add_file("src/pickled.v")
                self.add_depfileset(Spram(), "rtl")
                self.add_file("extra/lambda.v")
                self.add_define("SYNTHESIS")

        with self.active_dataroot("black_parrot"):
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
        ASICSynthesis.find_task(project).set("var", 'strategy', 'AREA3')
        ASICSynthesis.find_task(project).set("var", "flatten", False)
        ASICSynthesis.find_task(project).set("var", "abc_clock_derating", 0.95)

    def setup_asap7(self, project: ASIC):
        ASICSynthesis.find_task(project).set("var", 'strategy', 'AREA3')
        ASICSynthesis.find_task(project).set("var", "flatten", False)
        ASICSynthesis.find_task(project).set("var", "abc_clock_derating", 0.95)

    def setup_ihp130(self, project: ASIC):
        ASICSynthesis.find_task(project).set("var", 'strategy', 'AREA3')
        ASICSynthesis.find_task(project).set("var", "flatten", False)
        ASICSynthesis.find_task(project).set("var", "abc_clock_derating", 0.95)

    def setup_gf180(self, project: ASIC):
        ASICSynthesis.find_task(project).set("var", 'strategy', 'AREA3')
        ASICSynthesis.find_task(project).set("var", "flatten", False)
        ASICSynthesis.find_task(project).set("var", "abc_clock_derating", 0.95)

    def setup_skywater130(self, project: ASIC):
        ASICSynthesis.find_task(project).set("var", "flatten", False)
        ASICSynthesis.find_task(project).set("var", "abc_clock_derating", 0.95)


if __name__ == '__main__':
    project = ASIC(BlackParrotDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    asap7_demo(project)
    project.design.process_setups("asap7_asap7sc7p5t_rvt", project)

    project.run()
    project.summary()
