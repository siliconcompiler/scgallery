#!/usr/bin/env python3

from siliconcompiler import Design, ASICProject
from siliconcompiler.targets import asap7_demo


class BlinkyDesign(Design):
    def __init__(self):
        super().__init__("blinky")

        self.set_dataroot("extra", __file__)
        self.set_dataroot("blinky",
                          'git+https://github.com/fusesoc/blinky.git',
                          tag='b88a2a644723fc0c44827750fd054f09ce316b0b')

        with self.active_dataroot("blinky"):
            with self.active_fileset("rtl"):
                self.set_topmodule("blinky")
                self.add_file("blinky.v")
                self.set_param("clk_freq_hz", "1000000")

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


if __name__ == '__main__':
    project = ASICProject(BlinkyDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    asap7_demo(project)

    project.run()
    project.summary()
