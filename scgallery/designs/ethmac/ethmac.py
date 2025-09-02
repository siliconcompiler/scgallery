#!/usr/bin/env python3

from scgallery import GalleryDesign
from siliconcompiler import ASICProject
from siliconcompiler.targets import asap7_demo
from lambdalib.ramlib import Spram
from siliconcompiler.tools.slang.lint import Lint


class EthmacDesign(GalleryDesign):
    def __init__(self):
        super().__init__("ethmac")
        self.set_dataroot("ethmac", __file__)

        with self.active_dataroot("ethmac"):
            with self.active_fileset("rtl"):
                self.set_topmodule("ethmac")
                self.add_file([
                    'src/ethmac.v',
                    'src/ethmac_defines.v',
                    'src/eth_clockgen.v',
                    'src/eth_cop.v',
                    'src/eth_crc.v',
                    'src/eth_fifo.v',
                    'src/eth_maccontrol.v',
                    'src/eth_macstatus.v',
                    'src/eth_miim.v',
                    'src/eth_outputcontrol.v',
                    'src/eth_random.v',
                    'src/eth_receivecontrol.v',
                    'src/eth_register.v',
                    'src/eth_registers.v',
                    'src/eth_rxaddrcheck.v',
                    'src/eth_rxcounters.v',
                    'src/eth_rxethmac.v',
                    'src/eth_rxstatem.v',
                    'src/eth_shiftreg.v',
                    'src/eth_spram_256x32.v',
                    'src/eth_top.v',
                    'src/eth_transmitcontrol.v',
                    'src/eth_txcounters.v',
                    'src/eth_txethmac.v',
                    'src/eth_txstatem.v',
                    'src/eth_wishbone.v'])
                self.add_define("ETH_VIRTUAL_SILICON_RAM")
                self.add_file("extra/lambda.v")
                self.add_depfileset(Spram(), "rtl")
                self.add_idir("src")

        with self.active_dataroot("ethmac"):
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

        self.add_target_setup("lint", self.setup_lint)

    def setup_lint(self, project: ASICProject):
        lint_task: Lint = project.get_task(filter=Lint)
        if lint_task:
            lint_task.add_commandline_option(['--timescale', '1ns/1ns'])


if __name__ == '__main__':
    project = ASICProject(EthmacDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    project.load_target(asap7_demo.setup)

    project.run()
    project.summary()
