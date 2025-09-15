from siliconcompiler import Design
from scgallery import GalleryDesign
from siliconcompiler import ASICProject
from siliconcompiler.tools.openroad._apr import OpenROADGPLParameter
from siliconcompiler.flows.asicflow import ASICFlow
from siliconcompiler.tools.sv2v import convert


class SV2VFlow(ASICFlow):
    def __init__(self):
        super().__init__("asicflow-sv2v")
        self.insert_node("convert", convert.ConvertTask(), before_step="elaborate")


class _Base(Design):
    def __init__(self, name: str = None):
        super().__init__(name)
        self.set_dataroot("caliptra",
                          'git+https://github.com/chipsalliance/caliptra-rtl.git',
                          tag="v1.0")


class CaliptraTop(_Base):
    def __init__(self):
        super().__init__("caliptra_top_defines")
        with self.active_dataroot("caliptra"), self.active_fileset("rtl"):
            self.add_idir('src/integration/rtl')


class CaliptraLibs(_Base):
    def __init__(self):
        super().__init__("caliptra_libs")
        with self.active_dataroot("caliptra"), self.active_fileset("rtl"):
            self.add_file("src/libs/rtl/caliptra_sram.sv")
            self.add_file("src/libs/rtl/ahb_defines_pkg.sv")
            self.add_file("src/libs/rtl/caliptra_ahb_srom.sv")
            self.add_file("src/libs/rtl/apb_slv_sif.sv")
            self.add_file("src/libs/rtl/ahb_slv_sif.sv")
            self.add_file("src/libs/rtl/caliptra_icg.sv")
            self.add_file("src/libs/rtl/clk_gate.sv")
            self.add_file("src/libs/rtl/caliptra_2ff_sync.sv")
            self.add_file("src/libs/rtl/ahb_to_reg_adapter.sv")

            self.add_idir("src/libs/rtl")

            self.add_depfileset(CaliptraTop(), "rtl")


class DataVault(GalleryDesign, _Base):
    def __init__(self):
        super().__init__("caliptra_datavault")
        with self.active_dataroot("caliptra"), self.active_fileset("rtl"):
            self.set_topmodule("dv")
            self.add_file("src/datavault/rtl/dv_reg_pkg.sv")
            self.add_file("src/datavault/rtl/dv_reg.sv")
            self.add_file("src/datavault/rtl/dv_defines_pkg.sv")
            self.add_file("src/datavault/rtl/dv.sv")

            self.add_idir("src/datavault/rtl")

            self.add_depfileset(CaliptraLibs(), "rtl")

        self.set_dataroot("extra", __file__)
        with self.active_dataroot("extra"):
            with self.active_fileset("sdc.asap7sc7p5t_rvt"):
                self.add_file("constraints/datavault/asap7sc7p5t_rvt.sdc")

            with self.active_fileset("sdc.gf180mcu_fd_sc_mcu7t5v0_5LM"):
                self.add_file("constraints/datavault/gf180mcu_fd_sc_mcu7t5v0.sdc")

            with self.active_fileset("sdc.gf180mcu_fd_sc_mcu9t5v0_5LM"):
                self.add_file("constraints/datavault/gf180mcu_fd_sc_mcu9t5v0.sdc")

            with self.active_fileset("sdc.nangate45"):
                self.add_file("constraints/datavault/nangate45.sdc")

            with self.active_fileset("sdc.sg13g2_stdcell_1p2"):
                self.add_file("constraints/datavault/sg13g2_stdcell.sdc")

            with self.active_fileset("sdc.sky130hd"):
                self.add_file("constraints/datavault/sky130hd.sdc")

        self.add_target_setup("freepdk45_nangate45", self.setup_freepdk45)
        self.add_target_setup("asap7_asap7sc7p5t_rvt", self.setup_asap7)
        self.add_target_setup("ihp130_sg13g2_stdcell", self.setup_ihp130)
        self.add_target_setup("gf180_gf180mcu_fd_sc_mcu7t5v0", self.setup_gf180)
        self.add_target_setup("gf180_gf180mcu_fd_sc_mcu9t5v0", self.setup_gf180)
        self.add_target_setup("skywater130_sky130hd", self.setup_skywater130)

    def setup_freepdk45(self, project: ASICProject):
        project.set_flow(SV2VFlow())
        project.get_areaconstraints().set_density(30)
        for task in project.get_task(filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.40)

    def setup_asap7(self, project: ASICProject):
        project.set_flow(SV2VFlow())
        project.get_areaconstraints().set_density(30)
        for task in project.get_task(filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.40)

    def setup_ihp130(self, project: ASICProject):
        project.set_flow(SV2VFlow())
        project.get_areaconstraints().set_density(30)
        for task in project.get_task(filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.40)

    def setup_gf180(self, project: ASICProject):
        project.set_flow(SV2VFlow())
        project.get_areaconstraints().set_density(30)
        for task in project.get_task(filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.40)

    def setup_skywater130(self, project: ASICProject):
        project.set_flow(SV2VFlow())
        project.get_areaconstraints().set_density(30)
        for task in project.get_task(filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.40)


class KeyVault(GalleryDesign, _Base):
    def __init__(self):
        super().__init__("caliptra_keyvault")
        with self.active_dataroot("caliptra"), self.active_fileset("rtl"):
            self.set_topmodule("kv")
            self.add_file("src/keyvault/rtl/kv_reg_pkg.sv")
            self.add_file("src/keyvault/rtl/kv_reg.sv")
            self.add_file("src/keyvault/rtl/kv_defines_pkg.sv")
            self.add_file("src/keyvault/rtl/kv.sv")
            self.add_file("src/keyvault/rtl/kv_fsm.sv")
            self.add_file("src/keyvault/rtl/kv_read_client.sv")
            self.add_file("src/keyvault/rtl/kv_write_client.sv")

            self.add_idir("src/keyvault/rtl")

            self.add_depfileset(CaliptraLibs(), "rtl")

        self.set_dataroot("extra", __file__)
        with self.active_dataroot("extra"):
            with self.active_fileset("sdc.asap7sc7p5t_rvt"):
                self.add_file("constraints/keyvault/asap7sc7p5t_rvt.sdc")

            with self.active_fileset("sdc.gf180mcu_fd_sc_mcu7t5v0_5LM"):
                self.add_file("constraints/keyvault/gf180mcu_fd_sc_mcu7t5v0.sdc")

            with self.active_fileset("sdc.gf180mcu_fd_sc_mcu9t5v0_5LM"):
                self.add_file("constraints/keyvault/gf180mcu_fd_sc_mcu9t5v0.sdc")

            with self.active_fileset("sdc.nangate45"):
                self.add_file("constraints/keyvault/nangate45.sdc")

            with self.active_fileset("sdc.sg13g2_stdcell_1p2"):
                self.add_file("constraints/keyvault/sg13g2_stdcell.sdc")

            with self.active_fileset("sdc.sky130hd"):
                self.add_file("constraints/keyvault/sky130hd.sdc")

        self.add_target_setup("freepdk45_nangate45", self.setup_freepdk45)
        self.add_target_setup("asap7_asap7sc7p5t_rvt", self.setup_asap7)
        self.add_target_setup("ihp130_sg13g2_stdcell", self.setup_ihp130)
        self.add_target_setup("gf180_gf180mcu_fd_sc_mcu7t5v0", self.setup_gf180)
        self.add_target_setup("gf180_gf180mcu_fd_sc_mcu9t5v0", self.setup_gf180)
        self.add_target_setup("skywater130_sky130hd", self.setup_skywater130)

    def setup_freepdk45(self, project: ASICProject):
        project.set_flow(SV2VFlow())
        project.get_areaconstraints().set_density(20)
        for task in project.get_task(filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.25)

    def setup_asap7(self, project: ASICProject):
        project.set_flow(SV2VFlow())
        project.get_areaconstraints().set_density(20)
        for task in project.get_task(filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.25)

    def setup_ihp130(self, project: ASICProject):
        project.set_flow(SV2VFlow())
        project.get_areaconstraints().set_density(20)
        for task in project.get_task(filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.25)

    def setup_gf180(self, project: ASICProject):
        project.set_flow(SV2VFlow())
        project.get_areaconstraints().set_density(20)
        for task in project.get_task(filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.25)

    def setup_skywater130(self, project: ASICProject):
        project.set_flow(SV2VFlow())
        project.get_areaconstraints().set_density(20)
        for task in project.get_task(filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.25)


class PCRVault(_Base):
    def __init__(self):
        super().__init__("caliptra_pcrvault")
        with self.active_dataroot("caliptra"), self.active_fileset("rtl"):
            self.set_topmodule("kv")
            self.add_file("src/pcrvault/rtl/pv_reg_pkg.sv")
            self.add_file("src/pcrvault/rtl/pv_reg.sv")
            self.add_file("src/pcrvault/rtl/pv_defines_pkg.sv")
            self.add_file("src/pcrvault/rtl/pv.sv")
            self.add_file("src/pcrvault/rtl/pv_gen_hash.sv")

            self.add_idir("src/pcrvault/rtl")

            self.add_depfileset(CaliptraLibs(), "rtl")


class SHA512(GalleryDesign, _Base):
    def __init__(self):
        super().__init__("caliptra_sha512")
        with self.active_dataroot("caliptra"), self.active_fileset("rtl"):
            self.set_topmodule("sha512_ctrl")
            self.add_file("src/sha512/rtl/sha512_reg_pkg.sv")
            self.add_file("src/sha512/rtl/sha512_params_pkg.sv")
            self.add_file("src/sha512/rtl/sha512_ctrl.sv")
            self.add_file("src/sha512/rtl/sha512.sv")
            self.add_file("src/sha512/rtl/sha512_core.v")
            self.add_file("src/sha512/rtl/sha512_h_constants.v")
            self.add_file("src/sha512/rtl/sha512_k_constants.v")
            self.add_file("src/sha512/rtl/sha512_w_mem.v")
            self.add_file("src/sha512/rtl/sha512_reg.sv")

            self.add_idir("src/sha512/rtl")

            self.add_depfileset(CaliptraLibs(), "rtl")
            self.add_depfileset(PCRVault(), "rtl")
            self.add_depfileset(KeyVault(), "rtl")

        self.set_dataroot("extra", __file__)
        with self.active_dataroot("extra"):
            with self.active_fileset("sdc.asap7sc7p5t_rvt"):
                self.add_file("constraints/sha512/asap7sc7p5t_rvt.sdc")

            with self.active_fileset("sdc.gf180mcu_fd_sc_mcu7t5v0_5LM"):
                self.add_file("constraints/sha512/gf180mcu_fd_sc_mcu7t5v0.sdc")

            with self.active_fileset("sdc.gf180mcu_fd_sc_mcu9t5v0_5LM"):
                self.add_file("constraints/sha512/gf180mcu_fd_sc_mcu9t5v0.sdc")

            with self.active_fileset("sdc.nangate45"):
                self.add_file("constraints/sha512/nangate45.sdc")

            with self.active_fileset("sdc.sg13g2_stdcell_1p2"):
                self.add_file("constraints/sha512/sg13g2_stdcell.sdc")

            with self.active_fileset("sdc.sky130hd"):
                self.add_file("constraints/sha512/sky130hd.sdc")

        self.add_target_setup("freepdk45_nangate45", self.setup_freepdk45)
        self.add_target_setup("asap7_asap7sc7p5t_rvt", self.setup_asap7)
        self.add_target_setup("ihp130_sg13g2_stdcell", self.setup_ihp130)
        self.add_target_setup("gf180_gf180mcu_fd_sc_mcu7t5v0", self.setup_gf180)
        self.add_target_setup("gf180_gf180mcu_fd_sc_mcu9t5v0", self.setup_gf180)
        self.add_target_setup("skywater130_sky130hd", self.setup_skywater130)

    def setup_freepdk45(self, project: ASICProject):
        project.set_flow(SV2VFlow())
        project.get_areaconstraints().set_density(30)
        for task in project.get_task(filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.4)

    def setup_asap7(self, project: ASICProject):
        project.set_flow(SV2VFlow())
        project.get_areaconstraints().set_density(30)
        for task in project.get_task(filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.4)

    def setup_ihp130(self, project: ASICProject):
        project.set_flow(SV2VFlow())
        project.get_areaconstraints().set_density(30)
        for task in project.get_task(filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.4)

    def setup_gf180(self, project: ASICProject):
        project.set_flow(SV2VFlow())
        project.get_areaconstraints().set_density(30)
        for task in project.get_task(filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.4)

    def setup_skywater130(self, project: ASICProject):
        project.set_flow(SV2VFlow())
        project.get_areaconstraints().set_density(30)
        for task in project.get_task(filter=OpenROADGPLParameter):
            task.set("var", "place_density", 0.4)
