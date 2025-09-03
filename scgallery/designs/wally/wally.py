#!/usr/bin/env python3

import glob

import os.path

from scgallery import GalleryDesign
from siliconcompiler import ASICProject
from siliconcompiler.targets import asap7_demo
from lambdalib.ramlib import Spram
from siliconcompiler.tools.yosys.syn_asic import ASICSynthesis


class WallyDesign(GalleryDesign):
    def __init__(self):
        super().__init__("wally")
        self.set_dataroot("extra", __file__)
        self.set_dataroot("wally",
                          "git+https://github.com/openhwgroup/cvw",
                          tag="e0af0e68a32edd8eb98abc31c8b2b7b04fbd29b9")

        with self.active_fileset("rtl"):
            with self.active_dataroot("wally"):
                self.add_file("src/cvw.sv")
            with self.active_dataroot("extra"):
                self.set_topmodule("wallypipelinedcorewrapper")
                self.add_file("extra/wallypipelinedcorewrapper.sv")
            with self.active_dataroot("wally"):
                wally_path = self.get_dataroot("wally")

                for src in glob.glob(f'{wally_path}/src/*/*.sv'):
                    self.add_file(os.path.relpath(src, wally_path))

                for src in glob.glob(f'{wally_path}/src/*/*/*.sv'):
                    if not ('ram' in src and 'wbe_' in src):  # Exclude hardcoded SRAMs
                        self.add_file(os.path.relpath(src, wally_path))

                self.add_idir("config/shared")
            with self.active_dataroot("extra"):
                self.add_idir("extra/config")
                self.add_file("extra/lambda.v")
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
        project.get_task(filter=ASICSynthesis).set("var", "use_slang", True)
        project.get_task(filter=ASICSynthesis).set("var", "flatten", False)
        project.get_task(filter=ASICSynthesis).set("var", "auto_flatten", False)

    def setup_asap7(self, project: ASICProject):
        project.get_areaconstraints().set_density(30)
        project.get_task(filter=ASICSynthesis).set("var", "use_slang", True)
        project.get_task(filter=ASICSynthesis).set("var", "flatten", False)
        project.get_task(filter=ASICSynthesis).set("var", "auto_flatten", False)

    def setup_ihp130(self, project: ASICProject):
        project.get_task(filter=ASICSynthesis).set("var", "use_slang", True)
        project.get_task(filter=ASICSynthesis).set("var", "flatten", False)
        project.get_task(filter=ASICSynthesis).set("var", "auto_flatten", False)

    def setup_gf180(self, project: ASICProject):
        project.get_task(filter=ASICSynthesis).set("var", "use_slang", True)
        project.get_task(filter=ASICSynthesis).set("var", "flatten", False)
        project.get_task(filter=ASICSynthesis).set("var", "auto_flatten", False)

    def setup_skywater130(self, project: ASICProject):
        project.get_task(filter=ASICSynthesis).set("var", "use_slang", True)
        project.get_task(filter=ASICSynthesis).set("var", "flatten", False)
        project.get_task(filter=ASICSynthesis).set("var", "auto_flatten", False)


if __name__ == '__main__':
    project = ASICProject(WallyDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    project.load_target(asap7_demo.setup)
    project.design.process_setups("asap7_asap7sc7p5t_rvt", project)

    project.run()
    project.summary()
