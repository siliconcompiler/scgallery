#!/usr/bin/env python3

from siliconcompiler import ASICProject, Design
from siliconcompiler.targets import asap7_demo


class SERVDesign(Design):
    def __init__(self):
        super().__init__("serv")
        self.set_dataroot("root", __file__)
        self.set_dataroot("serv",
                          'git+https://github.com/olofk/serv.git',
                          'a72c1e8737d424c31bf6ff909795acc37aa4cc90')

        with self.active_dataroot("serv"):
            with self.active_fileset("rtl.serv_core"):
                self.add_file([
                    'rtl/serv_aligner.v',
                    'rtl/serv_alu.v',
                    'rtl/serv_bufreg2.v',
                    'rtl/serv_bufreg.v',
                    'rtl/serv_compdec.v',
                    'rtl/serv_csr.v',
                    'rtl/serv_ctrl.v',
                    'rtl/serv_debug.v',
                    'rtl/serv_decode.v',
                    'rtl/serv_immdec.v',
                    'rtl/serv_mem_if.v',
                    'rtl/serv_rf_if.v',
                    'rtl/serv_state.v',
                    'rtl/serv_top.v',
                    'rtl/serv_rf_ram_if.v'])
            with self.active_fileset("rtl"):
                self.set_topmodule("serv_synth_wrapper")
                self.add_file("rtl/serv_synth_wrapper.v")
                self.add_depfileset(self, "rtl.serv_core")

        with self.active_dataroot("root"):
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
    project = ASICProject(SERVDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    asap7_demo.setup(project)

    project.run()
    project.summary()
