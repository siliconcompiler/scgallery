#!/usr/bin/env python3

from siliconcompiler import ASICProject, Design
from siliconcompiler.targets import asap7_demo


class JPEGDesign(Design):
    def __init__(self):
        super().__init__("jpeg")
        self.set_dataroot("jpeg", __file__)

        with self.active_dataroot("jpeg"):
            with self.active_fileset("rtl"):
                self.set_topmodule("jpeg_encoder")
                self.add_file([
                    'src/jpeg_encoder.v',
                    'src/jpeg_qnr.v',
                    'src/jpeg_rle.v',
                    'src/jpeg_rle1.v',
                    'src/jpeg_rzs.v',
                    'src/dct.v',
                    'src/dct_mac.v',
                    'src/dctu.v',
                    'src/dctub.v',
                    'src/div_su.v',
                    'src/div_uu.v',
                    'src/fdct.v',
                    'src/zigzag.v'])
                self.add_idir("src/include")

        with self.active_dataroot("jpeg"):
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
    project = ASICProject(JPEGDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    project.load_target(asap7_demo.setup)

    project.run()
    project.summary()
