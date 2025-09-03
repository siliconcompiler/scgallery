#!/usr/bin/env python3

from scgallery import GalleryDesign
from siliconcompiler import ASICProject
from siliconcompiler.targets import asap7_demo

from siliconcompiler.flows.asicflow import ASICFlow
from siliconcompiler.tools.chisel import convert


class ChiselFlow(ASICFlow):
    def __init__(self):
        super().__init__("asicflow-chisel")
        self.remove_node("elaborate")
        self.node("convert", convert.ConvertTask())
        self.edge("convert", "synthesis")


class MockALUDesign(GalleryDesign):
    def __init__(self):
        super().__init__("mock_alu")
        self.set_dataroot("alu", __file__)
        with self.active_dataroot("alu"), self.active_fileset("rtl"):
            self.set_topmodule("MockAlu")
            self.add_file("src/build.sbt")

        self.set_dataroot("extra", __file__)
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

        self.add_target_setup("freepdk45_nangate45", self.setup_chisel)
        self.add_target_setup("asap7_asap7sc7p5t_rvt", self.setup_chisel)
        self.add_target_setup("ihp130_sg13g2_stdcell", self.setup_chisel)
        self.add_target_setup("gf180_gf180mcu_fd_sc_mcu7t5v0", self.setup_chisel)
        self.add_target_setup("gf180_gf180mcu_fd_sc_mcu9t5v0", self.setup_chisel)
        self.add_target_setup("skywater130_sky130hd", self.setup_chisel)

    def setup_chisel(self, project: ASICProject):
        project.set_flow(ChiselFlow())
        task = project.get_task(filter=convert.ConvertTask)
        task.set("var", "application", "GenerateMockAlu")

        task.add("var", "argument", ["--width", "64"])
        operations = [
            'ADD',
            'SUB',
            'AND',
            'OR',
            'XOR',
            'SHL',
            'SHR',
            'SRA',
            'SETCC_EQ',
            'SETCC_NE',
            'SETCC_LT',
            'SETCC_ULT',
            'SETCC_LE',
            'SETCC_ULE',
            'MULT']
        task.add("var", "argument", ["--operations", ",".join(operations)])
        task.add("var", "argument", ["--tech", "none"])


if __name__ == '__main__':
    project = ASICProject(MockALUDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    project.load_target(asap7_demo.setup)
    project.design.process_setups("asap7_asap7sc7p5t_rvt", project)

    project.run()
    project.summary()
