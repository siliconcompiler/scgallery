#!/usr/bin/env python3

from siliconcompiler import ASICProject, DesignSchema
from siliconcompiler.targets import asap7_demo


class UARTDesign(DesignSchema):
    def __init__(self):
        super().__init__("uart")
        self.set_dataroot("uart", __file__)

        with self.active_dataroot("uart"):
            with self.active_fileset("rtl"):
                self.set_topmodule("uart")
                self.add_file([
                    'src/uart.v',
                    'src/uart_tx.v',
                    'src/uart_rx.v'])

        with self.active_dataroot("uart"):
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
    project = ASICProject(UARTDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    project.load_target(asap7_demo.setup)

    project.run()
    project.summary()
