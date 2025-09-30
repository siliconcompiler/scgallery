#!/usr/bin/env python3

'''
Advanced Encryption Standard

Source: http://www.opencores.org/cores/aes_core/
'''

from scgallery import GalleryDesign
from siliconcompiler import ASIC
from siliconcompiler.targets import asap7_demo
from siliconcompiler.tools.openroad._apr import OpenROADGPLParameter
from siliconcompiler.tools import get_task


class AESDesign(GalleryDesign):
    def __init__(self):
        super().__init__("aes")

        self.set_dataroot("aes", __file__)

        with self.active_dataroot("aes"):
            with self.active_fileset("rtl"):
                self.set_topmodule("aes_cipher_top")
                self.add_file([
                    'src/aes_cipher_top.v',
                    'src/aes_inv_cipher_top.v',
                    'src/aes_inv_sbox.v',
                    'src/aes_key_expand_128.v',
                    'src/aes_rcon.v',
                    'src/aes_sbox.v'])
                self.add_idir("src")

        with self.active_dataroot("aes"):
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
        for task in get_task(project, filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.65)

    def setup_asap7(self, project: ASIC):
        project.constraint.area.set_density(25)
        for task in get_task(project, filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.65)

    def setup_ihp130(self, project: ASIC):
        for task in get_task(project, filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.65)

    def setup_gf180(self, project: ASIC):
        for task in get_task(project, filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.65)

    def setup_skywater130(self, project: ASIC):
        project.constraint.area.set_density(30)
        for task in get_task(project, filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.50)


if __name__ == '__main__':
    project = ASIC(AESDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    asap7_demo(project)
    project.design.process_setups("asap7_asap7sc7p5t_rvt", project)

    project.run()
    project.summary()
