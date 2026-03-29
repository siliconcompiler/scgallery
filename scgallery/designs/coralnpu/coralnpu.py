#!/usr/bin/env python3

"""
Coral NPU is a hardware accelerator for ML inferencing. Coral NPU is an Open Source IP designed
by Google Research and is freely available for integration into ultra-low-power System-on-Chips
(SoCs) targeting wearable devices such as hearables, augmented reality (AR) glasses and
smart watches.

Coral NPU is a neural processing unit (NPU), also known as an AI accelerator or deep-learning
processor. Coral NPU is based on the 32-bit RISC-V Instruction Set Architecture (ISA).

Coral NPU includes three distinct processor components that work together: matrix,
vector (SIMD), and scalar.

Source: https://github.com/google-coral/coralnpu/
"""

from scgallery import GalleryDesign
from siliconcompiler import ASIC
from siliconcompiler.targets import asap7_demo
from siliconcompiler.tools.yosys.syn_asic import ASICSynthesis
from lambdalib.ramlib import Spram


class CoralNPUDesign(GalleryDesign):
    def __init__(self):
        super().__init__("coralnpu")

        self.set_dataroot("gallery", __file__)
        self.set_dataroot(
            "opentitan",
            "git+https://github.com/lowRISC/opentitan.git",
            tag="f3b46add62acc0332e2d2d59d37298cf8cfb4d24",
        )
        self.set_dataroot(
            "coralnpu",
            "git+https://github.com/google-coral/coralnpu",
            tag="f33009468522a4d6f9845884a8c4c694e25c2997",
        )

        with self.active_fileset("rtl"):
            with self.active_dataroot("gallery"):
                self.set_topmodule("CoralNPUChiselSubsystem")
                self.add_define("SYNTHESIS")
                self.add_file("pickle/CoralNPUChiselSubsystem.sv")

            with self.active_dataroot("gallery"):
                self.add_file("extra/lambda.v")
                self.add_depfileset(Spram(), "rtl")

        with self.active_dataroot("gallery"):
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
        ASICSynthesis.find_task(project).set_yosys_useslang(True)
        ASICSynthesis.find_task(project).set_yosys_strategy("AREA0")
        ASICSynthesis.find_task(project).set_yosys_flatten(False)
        ASICSynthesis.find_task(project).set_yosys_abcclockderating(0.95)

    def setup_asap7(self, project: ASIC):
        ASICSynthesis.find_task(project).set_yosys_useslang(True)
        ASICSynthesis.find_task(project).set_yosys_strategy("AREA0")
        ASICSynthesis.find_task(project).set_yosys_flatten(False)
        ASICSynthesis.find_task(project).set_yosys_autoflatten(False)

    def setup_ihp130(self, project: ASIC):
        ASICSynthesis.find_task(project).set_yosys_useslang(True)
        ASICSynthesis.find_task(project).set_yosys_strategy("AREA0")
        ASICSynthesis.find_task(project).set_yosys_flatten(False)
        ASICSynthesis.find_task(project).set_yosys_abcclockderating(0.95)

    def setup_gf180(self, project: ASIC):
        ASICSynthesis.find_task(project).set_yosys_useslang(True)
        ASICSynthesis.find_task(project).set_yosys_strategy("AREA0")
        ASICSynthesis.find_task(project).set_yosys_flatten(False)
        ASICSynthesis.find_task(project).set_yosys_abcclockderating(0.95)

    def setup_skywater130(self, project: ASIC):
        ASICSynthesis.find_task(project).set_yosys_useslang(True)
        ASICSynthesis.find_task(project).set_yosys_strategy("AREA0")
        ASICSynthesis.find_task(project).set_yosys_flatten(False)
        ASICSynthesis.find_task(project).set_yosys_abcclockderating(0.95)


if __name__ == "__main__":
    project = ASIC(CoralNPUDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    asap7_demo(project)
    project.design.process_setups("asap7_asap7sc7p5t_rvt", project)

    project.run()
    project.summary()
