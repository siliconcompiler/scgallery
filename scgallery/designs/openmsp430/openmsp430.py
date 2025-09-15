#!/usr/bin/env python3

from siliconcompiler import ASICProject, Design
from siliconcompiler.targets import asap7_demo


class OpenMSP430Design(Design):
    def __init__(self):
        super().__init__("openmsp430")
        self.set_dataroot("extra", __file__)
        self.set_dataroot("openmsp430",
                          'git+https://github.com/olgirard/openmsp430.git',
                          tag='92c883abb4518dbc35b027e6cad5ffef5b2fbb81')

        with self.active_dataroot("openmsp430"):
            with self.active_fileset("rtl"):
                self.set_topmodule("openMSP430")
                self.add_file([
                    'core/rtl/verilog/openMSP430.v',
                    'core/rtl/verilog/omsp_frontend.v',
                    'core/rtl/verilog/omsp_execution_unit.v',
                    'core/rtl/verilog/omsp_register_file.v',
                    'core/rtl/verilog/omsp_alu.v',
                    'core/rtl/verilog/omsp_sfr.v',
                    'core/rtl/verilog/omsp_clock_module.v',
                    'core/rtl/verilog/omsp_mem_backbone.v',
                    'core/rtl/verilog/omsp_watchdog.v',
                    'core/rtl/verilog/omsp_dbg.v',
                    'core/rtl/verilog/omsp_dbg_uart.v',
                    'core/rtl/verilog/omsp_dbg_i2c.v',
                    'core/rtl/verilog/omsp_dbg_hwbrk.v',
                    'core/rtl/verilog/omsp_multiplier.v',
                    'core/rtl/verilog/omsp_sync_reset.v',
                    'core/rtl/verilog/omsp_sync_cell.v',
                    'core/rtl/verilog/omsp_scan_mux.v',
                    'core/rtl/verilog/omsp_and_gate.v',
                    'core/rtl/verilog/omsp_wakeup_cell.v',
                    'core/rtl/verilog/omsp_clock_gate.v',
                    'core/rtl/verilog/omsp_clock_mux.v'])

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
    project = ASICProject(OpenMSP430Design())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    project.load_target(asap7_demo.setup)

    project.run()
    project.summary()
