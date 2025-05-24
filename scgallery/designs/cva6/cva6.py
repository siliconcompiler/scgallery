#!/usr/bin/env python3

'''
The CORE-V CVA6 is an Application class 6-stage RISC-V CPU capable of booting Linux

Source: https://github.com/openhwgroup/cva6/
'''

from siliconcompiler import Chip
from siliconcompiler.targets import freepdk45_demo
from scgallery import Gallery

from lambdalib import ramlib

from siliconcompiler.tools import openroad
from siliconcompiler.tools._common import get_tool_tasks


def setup():
    chip = Chip('cva6')

    chip.register_source('cva6',
                         path='https://github.com/openhwgroup/cva6/archive/refs/tags/',
                         ref='v5.3.0')

    chip.register_source('cv-hpdcache',
                         path='git+https://github.com/openhwgroup/cv-hpdcache.git',
                         ref='04de80896981527c34fbbd35d7b1ef787a082d7c')

    chip.register_source('cvfpu',
                         path='git+https://github.com/openhwgroup/cvfpu.git',
                         ref='3116391bf66660f806b45e212b9949c528b4e270')

    target_config = 'cv32a65x'

    chip.input('core/include/config_pkg.sv', package='cva6')
    chip.input(f'core/include/{target_config}_config_pkg.sv', package='cva6')
    chip.input('core/include/riscv_pkg.sv', package='cva6')
    chip.input('core/include/ariane_pkg.sv', package='cva6')
    chip.input('vendor/pulp-platform/axi/src/axi_pkg.sv', package='cva6')
    chip.input('core/include/wt_cache_pkg.sv', package='cva6')
    chip.input('core/include/std_cache_pkg.sv', package='cva6')
    chip.input('core/include/build_config_pkg.sv', package='cva6')
    chip.input('core/cva6.sv', package='cva6')
    chip.input('core/cvxif_example/include/cvxif_instr_pkg.sv', package='cva6')
    chip.input('vendor/pulp-platform/common_cells/src/cf_math_pkg.sv', package='cva6')
    chip.input('rtl/src/hwpf_stride/hwpf_stride_pkg.sv', package='cv-hpdcache')
    chip.input('rtl/src/hpdcache_pkg.sv', package='cv-hpdcache')
    chip.input('src/fpnew_cast_multi.sv', package='cvfpu')
    chip.input('src/fpnew_classifier.sv', package='cvfpu')
    chip.input('src/fpnew_divsqrt_multi.sv', package='cvfpu')
    chip.input('src/fpnew_fma_multi.sv', package='cvfpu')
    chip.input('src/fpnew_fma.sv', package='cvfpu')
    chip.input('src/fpnew_noncomp.sv', package='cvfpu')
    chip.input('src/fpnew_opgroup_block.sv', package='cvfpu')
    chip.input('src/fpnew_opgroup_fmt_slice.sv', package='cvfpu')
    chip.input('src/fpnew_opgroup_multifmt_slice.sv', package='cvfpu')
    chip.input('src/fpnew_rounding.sv', package='cvfpu')
    chip.input('src/fpnew_top.sv', package='cvfpu')
    chip.input('src/fpu_div_sqrt_mvp/hdl/defs_div_sqrt_mvp.sv', package='cvfpu')
    chip.input('src/fpu_div_sqrt_mvp/hdl/control_mvp.sv', package='cvfpu')
    chip.input('src/fpu_div_sqrt_mvp/hdl/div_sqrt_top_mvp.sv', package='cvfpu')
    chip.input('src/fpu_div_sqrt_mvp/hdl/iteration_div_sqrt_mvp.sv', package='cvfpu')
    chip.input('src/fpu_div_sqrt_mvp/hdl/norm_div_sqrt_mvp.sv', package='cvfpu')
    chip.input('src/fpu_div_sqrt_mvp/hdl/nrbd_nrsc_mvp.sv', package='cvfpu')
    chip.input('src/fpu_div_sqrt_mvp/hdl/preprocess_mvp.sv', package='cvfpu')
    chip.input('core/cvxif_compressed_if_driver.sv', package='cva6')
    chip.input('core/cvxif_issue_register_commit_if_driver.sv', package='cva6')
    chip.input('core/cvxif_fu.sv', package='cva6')
    chip.input('core/cvxif_example/cvxif_example_coprocessor.sv', package='cva6')
    chip.input('core/cvxif_example/instr_decoder.sv', package='cva6')
    chip.input('core/cvxif_example/compressed_instr_decoder.sv', package='cva6')
    chip.input('core/cvxif_example/copro_alu.sv', package='cva6')
    chip.input('vendor/pulp-platform/common_cells/src/fifo_v3.sv', package='cva6')
    chip.input('vendor/pulp-platform/common_cells/src/lfsr.sv', package='cva6')
    chip.input('vendor/pulp-platform/common_cells/src/lfsr_8bit.sv', package='cva6')
    chip.input('vendor/pulp-platform/common_cells/src/stream_arbiter.sv', package='cva6')
    chip.input('vendor/pulp-platform/common_cells/src/stream_arbiter_flushable.sv', package='cva6')
    chip.input('vendor/pulp-platform/common_cells/src/stream_mux.sv', package='cva6')
    chip.input('vendor/pulp-platform/common_cells/src/stream_demux.sv', package='cva6')
    chip.input('vendor/pulp-platform/common_cells/src/lzc.sv', package='cva6')
    chip.input('vendor/pulp-platform/common_cells/src/rr_arb_tree.sv', package='cva6')
    chip.input('vendor/pulp-platform/common_cells/src/shift_reg.sv', package='cva6')
    chip.input('vendor/pulp-platform/common_cells/src/unread.sv', package='cva6')
    chip.input('vendor/pulp-platform/common_cells/src/popcount.sv', package='cva6')
    chip.input('vendor/pulp-platform/common_cells/src/exp_backoff.sv', package='cva6')
    chip.input('vendor/pulp-platform/common_cells/src/counter.sv', package='cva6')
    chip.input('vendor/pulp-platform/common_cells/src/delta_counter.sv', package='cva6')
    chip.input('core/cva6_rvfi_probes.sv', package='cva6')
    chip.input('core/alu.sv', package='cva6')
    chip.input('core/fpu_wrap.sv', package='cva6')
    chip.input('core/branch_unit.sv', package='cva6')
    chip.input('core/compressed_decoder.sv', package='cva6')
    chip.input('core/macro_decoder.sv', package='cva6')
    chip.input('core/controller.sv', package='cva6')
    chip.input('core/zcmt_decoder.sv', package='cva6')
    chip.input('core/csr_buffer.sv', package='cva6')
    chip.input('core/csr_regfile.sv', package='cva6')
    chip.input('core/decoder.sv', package='cva6')
    chip.input('core/ex_stage.sv', package='cva6')
    chip.input('core/instr_realign.sv', package='cva6')
    chip.input('core/id_stage.sv', package='cva6')
    chip.input('core/issue_read_operands.sv', package='cva6')
    chip.input('core/issue_stage.sv', package='cva6')
    chip.input('core/load_unit.sv', package='cva6')
    chip.input('core/load_store_unit.sv', package='cva6')
    chip.input('core/lsu_bypass.sv', package='cva6')
    chip.input('core/mult.sv', package='cva6')
    chip.input('core/multiplier.sv', package='cva6')
    chip.input('core/serdiv.sv', package='cva6')
    chip.input('core/perf_counters.sv', package='cva6')
    chip.input('core/ariane_regfile_ff.sv', package='cva6')
    chip.input('core/ariane_regfile_fpga.sv', package='cva6')
    chip.input('core/scoreboard.sv', package='cva6')
    chip.input('core/store_buffer.sv', package='cva6')
    chip.input('core/amo_buffer.sv', package='cva6')
    chip.input('core/store_unit.sv', package='cva6')
    chip.input('core/commit_stage.sv', package='cva6')
    chip.input('core/axi_shim.sv', package='cva6')
    chip.input('core/cva6_accel_first_pass_decoder_stub.sv', package='cva6')
    chip.input('core/cva6_fifo_v3.sv', package='cva6')
    chip.input('core/frontend/btb.sv', package='cva6')
    chip.input('core/frontend/bht.sv', package='cva6')
    chip.input('core/frontend/ras.sv', package='cva6')
    chip.input('core/frontend/instr_scan.sv', package='cva6')
    chip.input('core/frontend/instr_queue.sv', package='cva6')
    chip.input('core/frontend/frontend.sv', package='cva6')
    chip.input('core/cache_subsystem/wt_dcache_ctrl.sv', package='cva6')
    chip.input('core/cache_subsystem/wt_dcache_mem.sv', package='cva6')
    chip.input('core/cache_subsystem/wt_dcache_missunit.sv', package='cva6')
    chip.input('core/cache_subsystem/wt_dcache_wbuffer.sv', package='cva6')
    chip.input('core/cache_subsystem/wt_dcache.sv', package='cva6')
    chip.input('core/cache_subsystem/cva6_icache.sv', package='cva6')
    chip.input('core/cache_subsystem/wt_cache_subsystem.sv', package='cva6')
    chip.input('core/cache_subsystem/wt_axi_adapter.sv', package='cva6')
    chip.input('core/cache_subsystem/tag_cmp.sv', package='cva6')
    chip.input('core/cache_subsystem/axi_adapter.sv', package='cva6')
    chip.input('core/cache_subsystem/miss_handler.sv', package='cva6')
    chip.input('core/cache_subsystem/cache_ctrl.sv', package='cva6')
    chip.input('core/cache_subsystem/cva6_icache_axi_wrapper.sv', package='cva6')
    chip.input('core/cache_subsystem/std_cache_subsystem.sv', package='cva6')
    chip.input('core/cache_subsystem/std_nbdcache.sv', package='cva6')
    chip.input('rtl/src/utils/hpdcache_mem_resp_demux.sv', package='cv-hpdcache')
    chip.input('rtl/src/utils/hpdcache_mem_to_axi_read.sv', package='cv-hpdcache')
    chip.input('rtl/src/utils/hpdcache_mem_to_axi_write.sv', package='cv-hpdcache')
    chip.input('core/cache_subsystem/cva6_hpdcache_subsystem.sv', package='cva6')
    chip.input('core/cache_subsystem/cva6_hpdcache_subsystem_axi_arbiter.sv', package='cva6')
    chip.input('core/cache_subsystem/cva6_hpdcache_if_adapter.sv', package='cva6')
    chip.input('core/cache_subsystem/cva6_hpdcache_wrapper.sv', package='cva6')
    chip.input('core/pmp/src/pmp.sv', package='cva6')
    chip.input('core/pmp/src/pmp_entry.sv', package='cva6')
    chip.input('core/pmp/src/pmp_data_if.sv', package='cva6')
    chip.input('core/cva6_mmu/cva6_mmu.sv', package='cva6')
    chip.input('core/cva6_mmu/cva6_ptw.sv', package='cva6')
    chip.input('core/cva6_mmu/cva6_tlb.sv', package='cva6')
    chip.input('core/cva6_mmu/cva6_shared_tlb.sv', package='cva6')
    chip.input('rtl/src/utils/hpdcache_mem_req_read_arbiter.sv', package='cv-hpdcache')
    chip.input('rtl/src/utils/hpdcache_mem_req_write_arbiter.sv', package='cv-hpdcache')
    chip.input('rtl/src/common/hpdcache_demux.sv', package='cv-hpdcache')
    chip.input('rtl/src/common/hpdcache_lfsr.sv', package='cv-hpdcache')
    chip.input('rtl/src/common/hpdcache_sync_buffer.sv', package='cv-hpdcache')
    chip.input('rtl/src/common/hpdcache_fifo_reg.sv', package='cv-hpdcache')
    chip.input('rtl/src/common/hpdcache_fifo_reg_initialized.sv', package='cv-hpdcache')
    chip.input('rtl/src/common/hpdcache_fxarb.sv', package='cv-hpdcache')
    chip.input('rtl/src/common/hpdcache_rrarb.sv', package='cv-hpdcache')
    chip.input('rtl/src/common/hpdcache_mux.sv', package='cv-hpdcache')
    chip.input('rtl/src/common/hpdcache_decoder.sv', package='cv-hpdcache')
    chip.input('rtl/src/common/hpdcache_1hot_to_binary.sv', package='cv-hpdcache')
    chip.input('rtl/src/common/hpdcache_prio_1hot_encoder.sv', package='cv-hpdcache')
    chip.input('rtl/src/common/hpdcache_sram.sv', package='cv-hpdcache')
    chip.input('rtl/src/common/hpdcache_sram_wbyteenable.sv', package='cv-hpdcache')
    chip.input('rtl/src/common/hpdcache_regbank_wbyteenable_1rw.sv', package='cv-hpdcache')
    chip.input('rtl/src/common/hpdcache_regbank_wmask_1rw.sv', package='cv-hpdcache')
    chip.input('rtl/src/common/hpdcache_data_downsize.sv', package='cv-hpdcache')
    chip.input('rtl/src/common/hpdcache_data_upsize.sv', package='cv-hpdcache')
    chip.input('rtl/src/common/hpdcache_data_resize.sv', package='cv-hpdcache')
    chip.input('rtl/src/hwpf_stride/hwpf_stride.sv', package='cv-hpdcache')
    chip.input('rtl/src/hwpf_stride/hwpf_stride_arb.sv', package='cv-hpdcache')
    chip.input('rtl/src/hwpf_stride/hwpf_stride_wrapper.sv', package='cv-hpdcache')
    chip.input('rtl/src/hpdcache.sv', package='cv-hpdcache')
    chip.input('rtl/src/hpdcache_amo.sv', package='cv-hpdcache')
    chip.input('rtl/src/hpdcache_cmo.sv', package='cv-hpdcache')
    chip.input('rtl/src/hpdcache_core_arbiter.sv', package='cv-hpdcache')
    chip.input('rtl/src/hpdcache_ctrl.sv', package='cv-hpdcache')
    chip.input('rtl/src/hpdcache_ctrl_pe.sv', package='cv-hpdcache')
    chip.input('rtl/src/hpdcache_memctrl.sv', package='cv-hpdcache')
    chip.input('rtl/src/hpdcache_miss_handler.sv', package='cv-hpdcache')
    chip.input('rtl/src/hpdcache_mshr.sv', package='cv-hpdcache')
    chip.input('rtl/src/hpdcache_rtab.sv', package='cv-hpdcache')
    chip.input('rtl/src/hpdcache_uncached.sv', package='cv-hpdcache')
    chip.input('rtl/src/hpdcache_victim_plru.sv', package='cv-hpdcache')
    chip.input('rtl/src/hpdcache_victim_random.sv', package='cv-hpdcache')
    chip.input('rtl/src/hpdcache_victim_sel.sv', package='cv-hpdcache')
    chip.input('rtl/src/hpdcache_wbuf.sv', package='cv-hpdcache')
    chip.input('rtl/src/hpdcache_flush.sv', package='cv-hpdcache')

    chip.add('option', 'idir', 'core/include', package='cva6')
    chip.add('option', 'idir', 'vendor/pulp-platform/common_cells/include', package='cva6')
    chip.add('option', 'idir', 'rtl/include', package='cv-hpdcache')

    chip.set('option', 'define', 'HPDCACHE_ASSERT_OFF')

    chip.use(ramlib)
    chip.input('cva6/extra/hpdcache_sram_1rw.sv', package='scgallery-designs')
    chip.input('cva6/extra/hpdcache_sram_wbyteenable_1rw.sv', package='scgallery-designs')
    chip.input('cva6/extra/sram_cache.sv', package='scgallery-designs')

    return chip


def setup_physical(chip):
    chip.set('tool', 'sv2v', 'task', 'convert', 'var', 'skip_convert', True)
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'use_slang', True)

    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'flatten', False)

    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'abc_clock_derating', '0.95')

    for task in get_tool_tasks(chip, openroad):
        chip.set('tool', 'openroad', 'task', task, 'var', 'sta_define_path_groups', False)

    if chip.get('option', 'pdk') == 'asap7':
        for task in ('macro_placement', 'global_placement', 'pin_placement'):
            chip.set('tool', 'openroad', 'task', task, 'var', 'gpl_uniform_placement_adjustment',
                     '0.05')

        for task in ('global_place', 'global_route', 'repair_antenna'):
            chip.set('tool', 'openroad', 'task', task, 'var', 'M2_adjustment', '0.7')
            chip.set('tool', 'openroad', 'task', task, 'var', 'M3_adjustment', '0.6')


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=freepdk45_demo, module_path=__file__)
    setup_physical(chip)

    chip.run()
    chip.summary()
