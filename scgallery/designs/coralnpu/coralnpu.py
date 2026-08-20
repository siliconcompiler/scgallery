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

This builds RvvCoreMiniAxi, the vector core with an AXI interface, from the generated RTL
bundle published with each upstream release. The sources are split by function and the
libraries follow the module hierarchy, so the smaller cores can be built on their own by
depending on the library that carries them as its top module:

    coralnpu                  RvvCoreMiniAxi   AXI interface, fabric, debug, top
    |-- coralnpu_vector_core  RvvCoreMini      vector core integration
    |   |-- coralnpu_vector_backend            RVV backend, headers, helper cells
    |   `-- coralnpu_scalar_core  SCore        scalar pipeline
    |       |-- coralnpu_float                 fpnew, T-Head divide/sqrt, FloatCore
    |       |-- coralnpu_memories              TCM and SRAM wrappers, on la_spram
    |       `-- coralnpu_cells                 shared primitives, utility packages
    `-- coralnpu_memories

The file lists mirror filelist.f and firrtl_black_box_resource_files.f from the bundle,
without the verification/ layers, which hold the assertions and are not part of the design.
"""

from scgallery import GalleryDesign
from siliconcompiler import ASIC, Design
from siliconcompiler.targets import asap7_demo
from siliconcompiler.tools.yosys.syn_asic import ASICSynthesis
from lambdalib.ramlib import Spram

# The generated RTL is published as a release asset, it is not part of the
# repository: building it from the chisel sources needs bazel and a JVM
CORALNPU_RELEASE_TAG = "M3-2026-04-27"
CORALNPU_RELEASE = (
    "https://github.com/google-coral/coralnpu/releases/download/"
    f"{CORALNPU_RELEASE_TAG}/RvvCoreMiniAxi.zip"
)


class CoralNPULibrary(Design):
    """Base class for the libraries that make up Coral NPU.

    They all come from the same release bundle, and each declares the bundle
    root as an include directory because the sources include the headers that
    sit alongside them.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.set_dataroot("coralnpu", CORALNPU_RELEASE, tag=CORALNPU_RELEASE_TAG)


class CoralNPUCells(CoralNPULibrary):
    """Shared primitives: aligners, arbiters, clock gating and reset sync."""

    def __init__(self):
        super().__init__("coralnpu_cells")

        with self.active_fileset("rtl"):
            with self.active_dataroot("coralnpu"):
                self.add_idir('.')
                self.add_file([
                    'Aligner.sv',
                    'Aligner_119_4.sv',
                    'ClockGate.sv',
                    'RstSync.sv',
                    'cf_math_pkg.sv',
                    'compressor_3_2.sv',
                    'compressor_4_2.sv',
                    'dff.sv',
                    'edff_2d.sv',
                    'gated_clk_cell.v',
                    'handshake_multi_fifo.sv',
                    'lzc.sv',
                    'rr_arb_tree.sv'])


class CoralNPUFloat(CoralNPULibrary):
    """Floating point hardware: fpnew, the T-Head divide and square root units
    and the scalar FloatCore."""

    def __init__(self):
        super().__init__("coralnpu_float")

        with self.active_fileset("rtl"):
            self.add_depfileset(CoralNPUCells(), "rtl")
            with self.active_dataroot("coralnpu"):
                self.add_idir('.')
                # registers.svh carries the flop macros the T-Head sources use
                # without including it themselves
                self.add_file([
                    'registers.svh'], filetype="systemverilog")
                self.add_file([
                    'FRegfile.sv',
                    'FloatCore.sv',
                    'FloatCoreWrapper.sv',
                    'control_mvp.sv',
                    'ct_vfdsu_ctrl.v',
                    'ct_vfdsu_double.v',
                    'ct_vfdsu_ff1.v',
                    'ct_vfdsu_pack.v',
                    'ct_vfdsu_prepare.v',
                    'ct_vfdsu_round.v',
                    'ct_vfdsu_scalar_dp.v',
                    'ct_vfdsu_srt.v',
                    'ct_vfdsu_srt_radix16_bound_table.v',
                    'ct_vfdsu_srt_radix16_with_sqrt.v',
                    'ct_vfdsu_top.v',
                    'defs_div_sqrt_mvp.sv',
                    'div_sqrt_mvp_wrapper.sv',
                    'div_sqrt_top_mvp.sv',
                    'fpnew_cast_multi.sv',
                    'fpnew_classifier.sv',
                    'fpnew_divsqrt_multi.sv',
                    'fpnew_divsqrt_th_32.sv',
                    'fpnew_divsqrt_th_64_multi.sv',
                    'fpnew_fma.sv',
                    'fpnew_fma_multi.sv',
                    'fpnew_noncomp.sv',
                    'fpnew_opgroup_block.sv',
                    'fpnew_opgroup_fmt_slice.sv',
                    'fpnew_opgroup_multifmt_slice.sv',
                    'fpnew_pkg.sv',
                    'fpnew_rounding.sv',
                    'fpnew_top.sv',
                    'iteration_div_sqrt_mvp.sv',
                    'norm_div_sqrt_mvp.sv',
                    'nrbd_nrsc_mvp.sv',
                    'pa_fdsu_ctrl.v',
                    'pa_fdsu_ff1.v',
                    'pa_fdsu_pack_single.v',
                    'pa_fdsu_prepare.v',
                    'pa_fdsu_round_single.v',
                    'pa_fdsu_special.v',
                    'pa_fdsu_srt_single.v',
                    'pa_fdsu_top.v',
                    'pa_fpu_dp.v',
                    'pa_fpu_frbus.v',
                    'pa_fpu_src_type.v',
                    'preprocess_mvp.sv'])


class CoralNPUMemories(CoralNPULibrary):
    """The TCM and SRAM wrappers, mapped onto la_spram.

    Sram.v from the bundle is deliberately left out: it selects between vendor
    macros and a behavioral model, and extra/Sram.v replaces it with an
    la_spram instance so the memories harden for whichever PDK is targeted.
    """

    def __init__(self):
        super().__init__("coralnpu_memories")
        self.set_dataroot("extra", __file__)

        with self.active_fileset("rtl"):
            self.add_depfileset(Spram(), "rtl")
            with self.active_dataroot("extra"):
                self.add_file("extra/Sram.v")
            with self.active_dataroot("coralnpu"):
                self.add_idir('.')
                self.add_file([
                    'SRAM.sv',
                    'SRAM_1.sv',
                    'SRAM_2048x128.sv',
                    'SRAM_512x128.sv',
                    'TCM128.sv',
                    'TCM128_1.sv',
                    'ram_2x145.sv',
                    'ram_2x37.sv',
                    'ram_2x67.sv',
                    'ram_2x8.sv',
                    'ram_3x137.sv',
                    'ram_3x145.sv'])


class CoralNPUScalarCore(CoralNPULibrary):
    """The scalar pipeline: fetch, dispatch, execute, retire and the CSRs."""

    def __init__(self):
        super().__init__("coralnpu_scalar_core")

        with self.active_fileset("rtl"):
            self.set_topmodule("SCore")
            self.add_depfileset(CoralNPUCells(), "rtl")
            self.add_depfileset(CoralNPUFloat(), "rtl")
            self.add_depfileset(CoralNPUMemories(), "rtl")
            with self.active_dataroot("coralnpu"):
                self.add_idir('.')
                self.add_file([
                    'Alu.sv',
                    'Arbiter2_CsrCmd.sv',
                    'Arbiter4_MluCmd.sv',
                    'Arbiter5_RegfileWriteDataIO.sv',
                    'Bru.sv',
                    'Bru_1.sv',
                    'CircularBufferMulti.sv',
                    'CircularBufferMulti_1.sv',
                    'CircularBufferMulti_2.sv',
                    'Csr.sv',
                    'DispatchV2.sv',
                    'Dvu.sv',
                    'FaultManager.sv',
                    'FetchControl.sv',
                    'Fetcher.sv',
                    'InstructionBuffer.sv',
                    'LsuV2.sv',
                    'Mlu.sv',
                    'Queue1_FloatInstruction.sv',
                    'Queue1_MluStage1.sv',
                    'Queue1_MluStage2.sv',
                    'Queue1_UInt1.sv',
                    'Queue2_RegfileWriteDataIO.sv',
                    'Regfile.sv',
                    'RetirementBuffer.sv',
                    'SCore.sv',
                    'UncachedFetch.sv'])


class CoralNPUVectorBackend(CoralNPULibrary):
    """The RVV backend: decode, dispatch, the execution units and the vector
    register file."""

    def __init__(self):
        super().__init__("coralnpu_vector_backend")

        with self.active_fileset("rtl"):
            self.add_depfileset(CoralNPUCells(), "rtl")
            self.add_depfileset(CoralNPUFloat(), "rtl")
            # Vector configuration, matching the defines upstream builds this
            # bundle with in tests/cocotb/build_defs.bzl. TB_SUPPORT is not
            # optional here: RvvCoreWrapper.sv exposes the uop_pc and
            # last_uop_valid debug fields it guards as ports
            self.add_define("VLEN_128")
            self.add_define("ZVE32F_ON")
            self.add_define("TB_SUPPORT")
            with self.active_dataroot("coralnpu"):
                self.add_idir('.')
                # These headers carry macros and types used by sources that do
                # not include them themselves, so they are compiled up front
                self.add_file([
                    'rvv_backend.svh',
                    'rvv_backend_alu.svh',
                    'rvv_backend_dispatch.svh',
                    'rvv_backend_div.svh',
                    'rvv_backend_fma.svh',
                    'rvv_backend_pmtrdt.svh',
                    'rvv_backend_sva.svh'], filetype="systemverilog")
                self.add_file([
                    'adder.sv',
                    'arb_round_robin.sv',
                    'barrel_shifter.sv',
                    'cdffr.sv',
                    'edff.sv',
                    'handshake_ff.sv',
                    'multi_fifo.sv',
                    'rvv_backend.sv',
                    'rvv_backend_alu.sv',
                    'rvv_backend_alu_unit.sv',
                    'rvv_backend_alu_unit_addsub.sv',
                    'rvv_backend_alu_unit_execution_p1.sv',
                    'rvv_backend_alu_unit_mask.sv',
                    'rvv_backend_alu_unit_mask_viota.sv',
                    'rvv_backend_alu_unit_other.sv',
                    'rvv_backend_alu_unit_shift.sv',
                    'rvv_backend_arb.sv',
                    'rvv_backend_decode.sv',
                    'rvv_backend_decode_ctrl.sv',
                    'rvv_backend_decode_de2.sv',
                    'rvv_backend_decode_unit.sv',
                    'rvv_backend_decode_unit_ari.sv',
                    'rvv_backend_decode_unit_ari_de2.sv',
                    'rvv_backend_decode_unit_de2.sv',
                    'rvv_backend_decode_unit_lsu.sv',
                    'rvv_backend_decode_unit_lsu_de2.sv',
                    'rvv_backend_dispatch.sv',
                    'rvv_backend_dispatch_bypass.sv',
                    'rvv_backend_dispatch_ctrl.sv',
                    'rvv_backend_dispatch_operand.sv',
                    'rvv_backend_dispatch_opr_byte_type.sv',
                    'rvv_backend_dispatch_raw_uop_rob.sv',
                    'rvv_backend_dispatch_raw_uop_uop.sv',
                    'rvv_backend_dispatch_structure_hazard.sv',
                    'rvv_backend_div.sv',
                    'rvv_backend_div_unit.sv',
                    'rvv_backend_div_unit_divider.sv',
                    'rvv_backend_fdiv_wrapper.sv',
                    'rvv_backend_fma.sv',
                    'rvv_backend_fma_wrapper.sv',
                    'rvv_backend_freduction.sv',
                    'rvv_backend_lsu_remap.sv',
                    'rvv_backend_mac_unit.sv',
                    'rvv_backend_mul_unit_mul8.sv',
                    'rvv_backend_mulmac.sv',
                    'rvv_backend_pmtrdt.sv',
                    'rvv_backend_pmtrdt_unit.sv',
                    'rvv_backend_pmtrdt_unit_permutation.sv',
                    'rvv_backend_pmtrdt_unit_reduction.sv',
                    'rvv_backend_pmtrdt_unit_reduction_alu.sv',
                    'rvv_backend_retire.sv',
                    'rvv_backend_retire_waw.sv',
                    'rvv_backend_rob.sv',
                    'rvv_backend_sqrt7_rec7.sv',
                    'rvv_backend_vrf.sv',
                    'rvv_backend_vrf_reg.sv'])


class CoralNPUVectorCore(CoralNPULibrary):
    """Ties the scalar core to the vector backend."""

    def __init__(self):
        super().__init__("coralnpu_vector_core")

        with self.active_fileset("rtl"):
            self.set_topmodule("RvvCoreMini")
            self.add_depfileset(CoralNPUScalarCore(), "rtl")
            self.add_depfileset(CoralNPUVectorBackend(), "rtl")
            with self.active_dataroot("coralnpu"):
                self.add_idir('.')
                self.add_file([
                    'RvvCore.sv',
                    'RvvCoreMini.sv',
                    'RvvCoreShim.sv',
                    'RvvCoreWrapper.sv',
                    'RvvFrontEnd.sv'])


class CoralNPUDesign(CoralNPULibrary, GalleryDesign):
    def __init__(self):
        super().__init__("coralnpu")

        self.set_dataroot("gallery", __file__)

        with self.active_fileset("rtl"):
            self.set_topmodule("RvvCoreMiniAxi")
            self.add_define("SYNTHESIS")
            self.add_depfileset(CoralNPUVectorCore(), "rtl")
            self.add_depfileset(CoralNPUMemories(), "rtl")

            with self.active_dataroot("coralnpu"):
                self.add_idir('.')
                self.add_file([
                    'AxiSlave.sv',
                    'CoralNPURRArbiter.sv',
                    'CoralNPURRArbiter_1.sv',
                    'CoreCSR.sv',
                    'DBus2AxiV2.sv',
                    'DebugModule.sv',
                    'FabricArbiter.sv',
                    'FabricMux.sv',
                    'IBus2Axi.sv',
                    'Queue1_DebugModuleReqIO.sv',
                    'Queue1_DebugModuleRspIO.sv',
                    'Queue1_RWAxiAddress.sv',
                    'Queue2_AxiAddress.sv',
                    'Queue2_AxiWriteData.sv',
                    'Queue2_AxiWriteResponse.sv',
                    'Queue3_AxiReadData.sv',
                    'Queue3_AxiWriteData.sv',
                    'RvvCoreMiniAxi.sv'])

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

    def setup_asap7(self, project: ASIC):
        ASICSynthesis.find_task(project).set_yosys_useslang(True)

    def setup_ihp130(self, project: ASIC):
        ASICSynthesis.find_task(project).set_yosys_useslang(True)

    def setup_gf180(self, project: ASIC):
        ASICSynthesis.find_task(project).set_yosys_useslang(True)

    def setup_skywater130(self, project: ASIC):
        ASICSynthesis.find_task(project).set_yosys_useslang(True)


if __name__ == "__main__":
    project = ASIC(CoralNPUDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    asap7_demo(project)
    project.design.process_setups("asap7_asap7sc7p5t_rvt", project)

    project.run()
    project.summary()
