#!/usr/bin/env python3

'''
The CORE-V CVA6 is an Application class 6-stage RISC-V CPU capable of booting Linux

Source: https://github.com/openhwgroup/cva6/
'''

from scgallery import GalleryDesign
from siliconcompiler import ASICProject
from siliconcompiler.targets import asap7_demo
from siliconcompiler.tools.openroad._apr import OpenROADGPLParameter
from siliconcompiler.tools.yosys.syn_asic import ASICSynthesis
from lambdalib.ramlib import Spram


class CVA6Design(GalleryDesign):
    def __init__(self):
        super().__init__("cva6")

        self.set_dataroot("extra", __file__)
        self.set_dataroot("cva6",
                          'https://github.com/openhwgroup/cva6/archive/refs/tags/',
                          tag='v5.3.0')
        self.set_dataroot("cv-hpdcache",
                          'git+https://github.com/openhwgroup/cv-hpdcache.git',
                          tag='04de80896981527c34fbbd35d7b1ef787a082d7c')
        self.set_dataroot("cvfpu",
                          'git+https://github.com/openhwgroup/cvfpu.git',
                          tag='3116391bf66660f806b45e212b9949c528b4e270')

        target_config = 'cv32a65x'
        with self.active_fileset("rtl"):
            with self.active_dataroot("cva6"):
                self.set_topmodule("cva6")
                self.add_file([
                    'core/include/config_pkg.sv',
                    f'core/include/{target_config}_config_pkg.sv',
                    'core/include/riscv_pkg.sv',
                    'core/include/ariane_pkg.sv',
                    'vendor/pulp-platform/axi/src/axi_pkg.sv',
                    'core/include/wt_cache_pkg.sv',
                    'core/include/std_cache_pkg.sv',
                    'core/include/build_config_pkg.sv',
                    'core/cva6.sv',
                    'core/cvxif_example/include/cvxif_instr_pkg.sv',
                    'vendor/pulp-platform/common_cells/src/cf_math_pkg.sv'])

            with self.active_dataroot("cv-hpdcache"):
                self.add_file([
                    'rtl/src/hwpf_stride/hwpf_stride_pkg.sv',
                    'rtl/src/hpdcache_pkg.sv'])

            with self.active_dataroot("cvfpu"):
                self.add_file([
                    'src/fpnew_cast_multi.sv',
                    'src/fpnew_classifier.sv',
                    'src/fpnew_divsqrt_multi.sv',
                    'src/fpnew_fma_multi.sv',
                    'src/fpnew_fma.sv',
                    'src/fpnew_noncomp.sv',
                    'src/fpnew_opgroup_block.sv',
                    'src/fpnew_opgroup_fmt_slice.sv',
                    'src/fpnew_opgroup_multifmt_slice.sv',
                    'src/fpnew_rounding.sv',
                    'src/fpnew_top.sv',
                    'src/fpu_div_sqrt_mvp/hdl/defs_div_sqrt_mvp.sv',
                    'src/fpu_div_sqrt_mvp/hdl/control_mvp.sv',
                    'src/fpu_div_sqrt_mvp/hdl/div_sqrt_top_mvp.sv',
                    'src/fpu_div_sqrt_mvp/hdl/iteration_div_sqrt_mvp.sv',
                    'src/fpu_div_sqrt_mvp/hdl/norm_div_sqrt_mvp.sv',
                    'src/fpu_div_sqrt_mvp/hdl/nrbd_nrsc_mvp.sv',
                    'src/fpu_div_sqrt_mvp/hdl/preprocess_mvp.sv'])

            with self.active_dataroot("cva6"):
                self.add_file([
                    'core/cvxif_compressed_if_driver.sv',
                    'core/cvxif_issue_register_commit_if_driver.sv',
                    'core/cvxif_fu.sv',
                    'core/cvxif_example/cvxif_example_coprocessor.sv',
                    'core/cvxif_example/instr_decoder.sv',
                    'core/cvxif_example/compressed_instr_decoder.sv',
                    'core/cvxif_example/copro_alu.sv',
                    'vendor/pulp-platform/common_cells/src/fifo_v3.sv',
                    'vendor/pulp-platform/common_cells/src/lfsr.sv',
                    'vendor/pulp-platform/common_cells/src/lfsr_8bit.sv',
                    'vendor/pulp-platform/common_cells/src/stream_arbiter.sv',
                    'vendor/pulp-platform/common_cells/src/stream_arbiter_flushable.sv',
                    'vendor/pulp-platform/common_cells/src/stream_mux.sv',
                    'vendor/pulp-platform/common_cells/src/stream_demux.sv',
                    'vendor/pulp-platform/common_cells/src/lzc.sv',
                    'vendor/pulp-platform/common_cells/src/rr_arb_tree.sv',
                    'vendor/pulp-platform/common_cells/src/shift_reg.sv',
                    'vendor/pulp-platform/common_cells/src/unread.sv',
                    'vendor/pulp-platform/common_cells/src/popcount.sv',
                    'vendor/pulp-platform/common_cells/src/exp_backoff.sv',
                    'vendor/pulp-platform/common_cells/src/counter.sv',
                    'vendor/pulp-platform/common_cells/src/delta_counter.sv',
                    'core/cva6_rvfi_probes.sv',
                    'core/alu.sv',
                    'core/fpu_wrap.sv',
                    'core/branch_unit.sv',
                    'core/compressed_decoder.sv',
                    'core/macro_decoder.sv',
                    'core/controller.sv',
                    'core/zcmt_decoder.sv',
                    'core/csr_buffer.sv',
                    'core/csr_regfile.sv',
                    'core/decoder.sv',
                    'core/ex_stage.sv',
                    'core/instr_realign.sv',
                    'core/id_stage.sv',
                    'core/issue_read_operands.sv',
                    'core/issue_stage.sv',
                    'core/load_unit.sv',
                    'core/load_store_unit.sv',
                    'core/lsu_bypass.sv',
                    'core/mult.sv',
                    'core/multiplier.sv',
                    'core/serdiv.sv',
                    'core/perf_counters.sv',
                    'core/ariane_regfile_ff.sv',
                    'core/ariane_regfile_fpga.sv',
                    'core/scoreboard.sv',
                    'core/store_buffer.sv',
                    'core/amo_buffer.sv',
                    'core/store_unit.sv',
                    'core/commit_stage.sv',
                    'core/axi_shim.sv',
                    'core/cva6_accel_first_pass_decoder_stub.sv',
                    'core/cva6_fifo_v3.sv',
                    'core/frontend/btb.sv',
                    'core/frontend/bht.sv',
                    'core/frontend/ras.sv',
                    'core/frontend/instr_scan.sv',
                    'core/frontend/instr_queue.sv',
                    'core/frontend/frontend.sv',
                    'core/cache_subsystem/wt_dcache_ctrl.sv',
                    'core/cache_subsystem/wt_dcache_mem.sv',
                    'core/cache_subsystem/wt_dcache_missunit.sv',
                    'core/cache_subsystem/wt_dcache_wbuffer.sv',
                    'core/cache_subsystem/wt_dcache.sv',
                    'core/cache_subsystem/cva6_icache.sv',
                    'core/cache_subsystem/wt_cache_subsystem.sv',
                    'core/cache_subsystem/wt_axi_adapter.sv',
                    'core/cache_subsystem/tag_cmp.sv',
                    'core/cache_subsystem/axi_adapter.sv',
                    'core/cache_subsystem/miss_handler.sv',
                    'core/cache_subsystem/cache_ctrl.sv',
                    'core/cache_subsystem/cva6_icache_axi_wrapper.sv',
                    'core/cache_subsystem/std_cache_subsystem.sv',
                    'core/cache_subsystem/std_nbdcache.sv'])

            with self.active_dataroot("cv-hpdcache"):
                self.add_file([
                    'rtl/src/utils/hpdcache_mem_resp_demux.sv',
                    'rtl/src/utils/hpdcache_mem_to_axi_read.sv',
                    'rtl/src/utils/hpdcache_mem_to_axi_write.sv'])

            with self.active_dataroot("cva6"):
                self.add_file([
                    'core/cache_subsystem/cva6_hpdcache_subsystem.sv',
                    'core/cache_subsystem/cva6_hpdcache_subsystem_axi_arbiter.sv',
                    'core/cache_subsystem/cva6_hpdcache_if_adapter.sv',
                    'core/cache_subsystem/cva6_hpdcache_wrapper.sv',
                    'core/pmp/src/pmp.sv',
                    'core/pmp/src/pmp_entry.sv',
                    'core/pmp/src/pmp_data_if.sv',
                    'core/cva6_mmu/cva6_mmu.sv',
                    'core/cva6_mmu/cva6_ptw.sv',
                    'core/cva6_mmu/cva6_tlb.sv',
                    'core/cva6_mmu/cva6_shared_tlb.sv'])

            with self.active_dataroot("cv-hpdcache"):
                self.add_file([
                    'rtl/src/utils/hpdcache_mem_req_read_arbiter.sv',
                    'rtl/src/utils/hpdcache_mem_req_write_arbiter.sv',
                    'rtl/src/common/hpdcache_demux.sv',
                    'rtl/src/common/hpdcache_lfsr.sv',
                    'rtl/src/common/hpdcache_sync_buffer.sv',
                    'rtl/src/common/hpdcache_fifo_reg.sv',
                    'rtl/src/common/hpdcache_fifo_reg_initialized.sv',
                    'rtl/src/common/hpdcache_fxarb.sv',
                    'rtl/src/common/hpdcache_rrarb.sv',
                    'rtl/src/common/hpdcache_mux.sv',
                    'rtl/src/common/hpdcache_decoder.sv',
                    'rtl/src/common/hpdcache_1hot_to_binary.sv',
                    'rtl/src/common/hpdcache_prio_1hot_encoder.sv',
                    'rtl/src/common/hpdcache_sram.sv',
                    'rtl/src/common/hpdcache_sram_wbyteenable.sv',
                    'rtl/src/common/hpdcache_regbank_wbyteenable_1rw.sv',
                    'rtl/src/common/hpdcache_regbank_wmask_1rw.sv',
                    'rtl/src/common/hpdcache_data_downsize.sv',
                    'rtl/src/common/hpdcache_data_upsize.sv',
                    'rtl/src/common/hpdcache_data_resize.sv',
                    'rtl/src/hwpf_stride/hwpf_stride.sv',
                    'rtl/src/hwpf_stride/hwpf_stride_arb.sv',
                    'rtl/src/hwpf_stride/hwpf_stride_wrapper.sv',
                    'rtl/src/hpdcache.sv',
                    'rtl/src/hpdcache_amo.sv',
                    'rtl/src/hpdcache_cmo.sv',
                    'rtl/src/hpdcache_core_arbiter.sv',
                    'rtl/src/hpdcache_ctrl.sv',
                    'rtl/src/hpdcache_ctrl_pe.sv',
                    'rtl/src/hpdcache_memctrl.sv',
                    'rtl/src/hpdcache_miss_handler.sv',
                    'rtl/src/hpdcache_mshr.sv',
                    'rtl/src/hpdcache_rtab.sv',
                    'rtl/src/hpdcache_uncached.sv',
                    'rtl/src/hpdcache_victim_plru.sv',
                    'rtl/src/hpdcache_victim_random.sv',
                    'rtl/src/hpdcache_victim_sel.sv',
                    'rtl/src/hpdcache_wbuf.sv',
                    'rtl/src/hpdcache_flush.sv'])

            with self.active_dataroot("cva6"):
                self.add_idir("core/include")
                self.add_idir("vendor/pulp-platform/common_cells/include")

            with self.active_dataroot("cv-hpdcache"):
                self.add_idir("rtl/include")

            self.add_define("HPDCACHE_ASSERT_OFF")

            self.add_depfileset(Spram(), "rtl")

            with self.active_dataroot("extra"):
                self.add_file("extra/hpdcache_sram_1rw.sv")
                self.add_file("extra/hpdcache_sram_wbyteenable_1rw.sv")
                self.add_file("extra/sram_cache.sv")

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

        self.add_target_setup("freepdk45_nangate45", self.setup_freepdk45)
        self.add_target_setup("asap7_asap7sc7p5t_rvt", self.setup_asap7)
        self.add_target_setup("ihp130_sg13g2_stdcell", self.setup_ihp130)
        self.add_target_setup("gf180_gf180mcu_fd_sc_mcu7t5v0", self.setup_gf180)
        self.add_target_setup("gf180_gf180mcu_fd_sc_mcu9t5v0", self.setup_gf180)
        self.add_target_setup("skywater130_sky130hd", self.setup_skywater130)

    def setup_freepdk45(self, project: ASICProject):
        project.get_task(filter=ASICSynthesis).set("var", "use_slang", True)
        project.get_task(filter=ASICSynthesis).set("var", "flatten", False)
        project.get_task(filter=ASICSynthesis).set("var", "abc_clock_derating", 0.95)

    def setup_asap7(self, project: ASICProject):
        project.get_task(filter=ASICSynthesis).set("var", "use_slang", True)
        project.get_task(filter=ASICSynthesis).set("var", "flatten", False)
        project.get_task(filter=ASICSynthesis).set("var", "abc_clock_derating", 0.95)

        for task in project.get_task(filter=OpenROADGPLParameter):
            task.set("var", "gpl_uniform_placement_adjustment", "0.05")

    def setup_ihp130(self, project: ASICProject):
        project.get_task(filter=ASICSynthesis).set("var", "use_slang", True)
        project.get_task(filter=ASICSynthesis).set("var", "flatten", False)
        project.get_task(filter=ASICSynthesis).set("var", "abc_clock_derating", 0.95)

    def setup_gf180(self, project: ASICProject):
        project.get_task(filter=ASICSynthesis).set("var", "use_slang", True)
        project.get_task(filter=ASICSynthesis).set("var", "flatten", False)
        project.get_task(filter=ASICSynthesis).set("var", "abc_clock_derating", 0.95)

    def setup_skywater130(self, project: ASICProject):
        project.get_task(filter=ASICSynthesis).set("var", "use_slang", True)
        project.get_task(filter=ASICSynthesis).set("var", "flatten", False)
        project.get_task(filter=ASICSynthesis).set("var", "abc_clock_derating", 0.95)


if __name__ == '__main__':
    project = ASICProject(CVA6Design())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    project.load_target(asap7_demo.setup)
    project.design.process_setups("asap7_asap7sc7p5t_rvt", project)

    project.run()
    project.summary()
