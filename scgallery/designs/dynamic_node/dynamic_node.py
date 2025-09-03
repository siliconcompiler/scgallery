#!/usr/bin/env python3

from siliconcompiler import DesignSchema, ASICProject
from siliconcompiler.targets import asap7_demo


class DynamicNodeDesign(DesignSchema):
    def __init__(self):
        super().__init__("dynamic_node")

        self.set_dataroot("extra", __file__)
        self.set_dataroot("OPDB",
                          'git+https://github.com/PrincetonUniversity/OPDB.git',
                          tag='a80e536ba29779faed68e32d4a202f6b7a93bc9b')

        with self.active_dataroot("OPDB"):
            with self.active_fileset("rtl"):
                self.set_topmodule("dynamic_node_top_wrap")
                self.add_file("modules/dynamic_node_2dmesh/NETWORK_2dmesh/dynamic_node_2dmesh.pickle.v")

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
    project = ASICProject(DynamicNodeDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    project.load_target(asap7_demo.setup)

    project.run()
    project.summary()
