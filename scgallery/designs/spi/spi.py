#!/usr/bin/env python3

from siliconcompiler import ASICProject, Design
from siliconcompiler.targets import asap7_demo


class SPIDesign(Design):
    def __init__(self):
        super().__init__("spi")
        self.set_dataroot("spi", __file__)

        with self.active_dataroot("spi"):
            with self.active_fileset("rtl"):
                self.set_topmodule("spi")
                self.add_file("src/spi.v")

        with self.active_dataroot("spi"):
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


if __name__ == '__main__':
    project = ASICProject(SPIDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    asap7_demo.setup(project)

    project.run()
    project.summary()
