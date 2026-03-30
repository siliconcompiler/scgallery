#!/usr/bin/env python3

from scgallery import GalleryDesign
from siliconcompiler import ASIC
from siliconcompiler.targets import asap7_demo
from lambdalib.ramlib import Spram
from siliconcompiler.tools.openroad.macro_placement import MacroPlacementTask


class Riscv32iDesign(GalleryDesign):
    def __init__(self):
        super().__init__("riscv32i")
        self.set_dataroot("riscv32i", __file__)

        with self.active_dataroot("riscv32i"):
            with self.active_fileset("rtl"):
                self.set_topmodule("riscv_top")
                self.add_file([
                    'src/adder.v',
                    'src/alu.v',
                    'src/aludec.v',
                    'src/controller.v',
                    'src/datapath.v',
                    'src/dmem.v',
                    'src/flopenr.v',
                    'src/flopens.v',
                    'src/flopr.v',
                    'src/magcompare2b.v',
                    'src/magcompare2c.v',
                    'src/magcompare32.v',
                    'src/maindec.v',
                    'src/mux2.v',
                    'src/mux3.v',
                    'src/mux4.v',
                    'src/mux5.v',
                    'src/mux8.v',
                    'src/regfile.v',
                    'src/riscv.v',
                    'src/rom.v',
                    'src/shifter.v',
                    'src/signext.v',
                    'src/top.v'])
                self.add_depfileset(Spram(), "rtl")

        with self.active_dataroot("riscv32i"):
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

    def setup_freepdk45(self, project: ASIC):
        MacroPlacementTask.find_task(project).set_openroad_macroplacehalo(10, 10)


if __name__ == '__main__':
    project = ASIC(Riscv32iDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    asap7_demo(project)

    project.run()
    project.summary()
