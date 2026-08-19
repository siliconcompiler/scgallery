#!/usr/bin/env python3

'''
Source: https://github.com/black-parrot/black-parrot

A single core BlackParrot (bp_unicore_lite) in the miniparrot configuration.

The sources are split into one library per upstream source tree, tied together
with add_depfileset:

    black_parrot (bp_top)  -> bp_fe, bp_be, bp_me
    bp_fe, bp_me           -> bp_common
    bp_be                  -> bp_common, hardfloat
    bp_common              -> basejump_stl
    basejump_stl           -> bsg_lambda_mem -> la_spram

Every file list mirrors the matching section of bp_top/flist.vcs.
'''

from scgallery import GalleryDesign
from siliconcompiler import ASIC, Design
from siliconcompiler.targets import asap7_demo
from siliconcompiler.tools.yosys.syn_asic import ASICSynthesis
from lambdalib.ramlib import Spram

BLACK_PARROT_REPO = 'git+https://github.com/black-parrot/black-parrot.git'
BLACK_PARROT_TAG = 'f91010f654a5dfd00f83dbe25dbda482218d540b'


class BlackParrotLibrary(GalleryDesign):
    """Base class for the libraries that make up BlackParrot, and the design
    itself, so that the source repository is declared in one place.

    Everything comes from the same repository, basejump_stl and HardFloat are
    pulled in as submodules of it.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.set_dataroot("black-parrot", BLACK_PARROT_REPO, tag=BLACK_PARROT_TAG)


class BSGLambdaMemories(Design):
    """Hardened replacements for the basejump_stl memory primitives.

    Memories large enough to be worth hardening are mapped onto la_spram,
    smaller ones fall back to the basejump_stl behavioral models. These files
    replace the equivalents in basejump_stl, which are left out of its fileset.
    """

    def __init__(self):
        super().__init__("bsg_lambda_mem")
        self.set_dataroot("extra", __file__)

        with self.active_fileset("rtl"):
            self.add_depfileset(Spram(), "rtl")
            with self.active_dataroot("extra"):
                self.add_file([
                    'extra/bsg_mem_1rw_sync.sv',
                    'extra/bsg_mem_1rw_sync_mask_write_bit.sv',
                    'extra/bsg_mem_1rw_sync_mask_write_byte.sv'])


class BaseJumpSTL(BlackParrotLibrary):
    """BaseJump STL, the standard library BlackParrot is built on."""

    def __init__(self):
        super().__init__("basejump_stl")

        with self.active_fileset("rtl"):
            self.add_depfileset(BSGLambdaMemories(), "rtl")
            with self.active_dataroot("black-parrot"):
                self.add_idir([
                    'external/basejump_stl/bsg_cache',
                    'external/basejump_stl/bsg_dataflow',
                    'external/basejump_stl/bsg_dmc',
                    'external/basejump_stl/bsg_mem',
                    'external/basejump_stl/bsg_misc',
                    'external/basejump_stl/bsg_test',
                    'external/basejump_stl/bsg_noc'])
                # Packages
                self.add_file([
                    'external/basejump_stl/bsg_axi/bsg_axi_pkg.sv',
                    'external/basejump_stl/bsg_cache/bsg_cache_pkg.sv',
                    'external/basejump_stl/bsg_noc/bsg_noc_pkg.sv',
                    'external/basejump_stl/bsg_noc/bsg_wormhole_router_pkg.sv'])
                self.add_file([
                    'external/basejump_stl/bsg_async/bsg_async_fifo.sv',
                    'external/basejump_stl/bsg_async/bsg_launch_sync_sync.sv',
                    'external/basejump_stl/bsg_async/bsg_sync_sync.sv',
                    'external/basejump_stl/bsg_async/bsg_async_ptr_gray.sv',
                    'external/basejump_stl/bsg_cache/bsg_cache.sv',
                    'external/basejump_stl/bsg_cache/bsg_cache_dma.sv',
                    'external/basejump_stl/bsg_cache/bsg_cache_dma_to_wormhole.sv',
                    'external/basejump_stl/bsg_cache/bsg_cache_miss.sv',
                    'external/basejump_stl/bsg_cache/bsg_cache_decode.sv',
                    'external/basejump_stl/bsg_cache/bsg_cache_sbuf.sv',
                    'external/basejump_stl/bsg_cache/bsg_cache_tbuf.sv',
                    'external/basejump_stl/bsg_cache/bsg_cache_buffer_queue.sv',
                    'external/basejump_stl/bsg_cache/bsg_wormhole_to_cache_dma_fanout.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_channel_tunnel.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_channel_tunnel_in.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_channel_tunnel_out.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_1_to_n_tagged_fifo.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_1_to_n_tagged.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_fifo_1r1w_large.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_fifo_1r1w_pseudo_large.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_fifo_1r1w_small.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_fifo_1r1w_small_unhardened.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_fifo_1r1w_small_hardened.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_fifo_1rw_large.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_fifo_tracker.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_flow_counter.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_one_fifo.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_parallel_in_serial_out.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_parallel_in_serial_out_dynamic.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_parallel_in_serial_out_passthrough.sv',
                    'bp_common/src/v/bsg_parallel_in_serial_out_passthrough_dynamic.sv',
                    'bp_common/src/v/bsg_serial_in_parallel_out_passthrough_dynamic.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_round_robin_1_to_n.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_round_robin_2_to_2.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_round_robin_n_to_1.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_serial_in_parallel_out.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_serial_in_parallel_out_dynamic.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_serial_in_parallel_out_full.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_serial_in_parallel_out_passthrough.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_shift_reg.sv',
                    'external/basejump_stl/bsg_dataflow/bsg_two_fifo.sv',
                    'external/basejump_stl/bsg_mem/bsg_cam_1r1w_replacement.sv',
                    'external/basejump_stl/bsg_mem/bsg_cam_1r1w_sync.sv',
                    'external/basejump_stl/bsg_mem/bsg_cam_1r1w_tag_array.sv',
                    'external/basejump_stl/bsg_mem/bsg_mem_1r1w.sv',
                    'external/basejump_stl/bsg_mem/bsg_mem_1r1w_one_hot.sv',
                    'external/basejump_stl/bsg_mem/bsg_mem_1r1w_sync_synth.sv',
                    'external/basejump_stl/bsg_mem/bsg_mem_1r1w_sync.sv',
                    'external/basejump_stl/bsg_mem/bsg_mem_1r1w_synth.sv',
                    'external/basejump_stl/bsg_mem/bsg_mem_1rw_sync_mask_write_bit_synth.sv',
                    'external/basejump_stl/bsg_mem/bsg_mem_1rw_sync_mask_write_byte_synth.sv',
                    'external/basejump_stl/bsg_mem/bsg_mem_1rw_sync_synth.sv',
                    'external/basejump_stl/bsg_mem/bsg_mem_2r1w_sync.sv',
                    'external/basejump_stl/bsg_mem/bsg_mem_2r1w_sync_synth.sv',
                    'external/basejump_stl/bsg_mem/bsg_mem_3r1w_sync.sv',
                    'external/basejump_stl/bsg_mem/bsg_mem_3r1w_sync_synth.sv',
                    'external/basejump_stl/bsg_misc/bsg_adder_cin.sv',
                    'external/basejump_stl/bsg_misc/bsg_adder_one_hot.sv',
                    'external/basejump_stl/bsg_misc/bsg_adder_ripple_carry.sv',
                    'external/basejump_stl/bsg_misc/bsg_arb_fixed.sv',
                    'external/basejump_stl/bsg_misc/bsg_arb_round_robin.sv',
                    'external/basejump_stl/bsg_misc/bsg_array_concentrate_static.sv',
                    'external/basejump_stl/bsg_misc/bsg_buf.sv',
                    'external/basejump_stl/bsg_misc/bsg_buf_ctrl.sv',
                    'external/basejump_stl/bsg_misc/bsg_circular_ptr.sv',
                    'external/basejump_stl/bsg_misc/bsg_concentrate_static.sv',
                    'external/basejump_stl/bsg_misc/bsg_counting_leading_zeros.sv',
                    'external/basejump_stl/bsg_misc/bsg_counter_clear_up.sv',
                    'external/basejump_stl/bsg_misc/bsg_counter_clear_up_one_hot.sv',
                    'external/basejump_stl/bsg_misc/bsg_counter_clock_downsample.sv',
                    'external/basejump_stl/bsg_misc/bsg_counter_set_down.sv',
                    'external/basejump_stl/bsg_misc/bsg_counter_set_en.sv',
                    'external/basejump_stl/bsg_misc/bsg_counter_up_down.sv',
                    'external/basejump_stl/bsg_misc/bsg_counter_up_down_variable.sv',
                    'external/basejump_stl/bsg_misc/bsg_crossbar_o_by_i.sv',
                    'external/basejump_stl/bsg_misc/bsg_crossbar_control_locking_o_by_i.sv',
                    'external/basejump_stl/bsg_misc/bsg_cycle_counter.sv',
                    'external/basejump_stl/bsg_misc/bsg_decode.sv',
                    'external/basejump_stl/bsg_misc/bsg_decode_with_v.sv',
                    'external/basejump_stl/bsg_misc/bsg_dff.sv',
                    'external/basejump_stl/bsg_misc/bsg_dff_chain.sv',
                    'external/basejump_stl/bsg_misc/bsg_dff_en.sv',
                    'external/basejump_stl/bsg_misc/bsg_dff_en_bypass.sv',
                    'external/basejump_stl/bsg_misc/bsg_dff_reset.sv',
                    'external/basejump_stl/bsg_misc/bsg_dff_reset_en.sv',
                    'external/basejump_stl/bsg_misc/bsg_dff_reset_en_bypass.sv',
                    'external/basejump_stl/bsg_misc/bsg_dff_reset_set_clear.sv',
                    'external/basejump_stl/bsg_misc/bsg_dlatch.sv',
                    'external/basejump_stl/bsg_misc/bsg_edge_detect.sv',
                    'external/basejump_stl/bsg_misc/bsg_encode_one_hot.sv',
                    'external/basejump_stl/bsg_misc/bsg_expand_bitmask.sv',
                    'external/basejump_stl/bsg_misc/bsg_gray_to_binary.sv',
                    'external/basejump_stl/bsg_misc/bsg_hash_bank.sv',
                    'external/basejump_stl/bsg_misc/bsg_hash_bank_reverse.sv',
                    'external/basejump_stl/bsg_misc/bsg_imul_iterative.sv',
                    'external/basejump_stl/bsg_misc/bsg_idiv_iterative.sv',
                    'external/basejump_stl/bsg_misc/bsg_idiv_iterative_controller.sv',
                    'external/basejump_stl/bsg_misc/bsg_lfsr.sv',
                    'external/basejump_stl/bsg_misc/bsg_lru_pseudo_tree_backup.sv',
                    'external/basejump_stl/bsg_misc/bsg_lru_pseudo_tree_decode.sv',
                    'external/basejump_stl/bsg_misc/bsg_lru_pseudo_tree_encode.sv',
                    'external/basejump_stl/bsg_misc/bsg_locking_arb_fixed.sv',
                    'external/basejump_stl/bsg_misc/bsg_mul_add_unsigned.sv',
                    'external/basejump_stl/bsg_misc/bsg_mux.sv',
                    'external/basejump_stl/bsg_misc/bsg_mux_bitwise.sv',
                    'external/basejump_stl/bsg_misc/bsg_mux_butterfly.sv',
                    'external/basejump_stl/bsg_misc/bsg_mux_one_hot.sv',
                    'external/basejump_stl/bsg_misc/bsg_mux_segmented.sv',
                    'external/basejump_stl/bsg_misc/bsg_muxi2_gatestack.sv',
                    'external/basejump_stl/bsg_misc/bsg_nor2.sv',
                    'external/basejump_stl/bsg_misc/bsg_nor3.sv',
                    'external/basejump_stl/bsg_misc/bsg_nand.sv',
                    'external/basejump_stl/bsg_misc/bsg_popcount.sv',
                    'external/basejump_stl/bsg_misc/bsg_priority_encode.sv',
                    'external/basejump_stl/bsg_misc/bsg_priority_encode_one_hot_out.sv',
                    'external/basejump_stl/bsg_misc/bsg_reduce.sv',
                    'external/basejump_stl/bsg_misc/bsg_reduce_segmented.sv',
                    'external/basejump_stl/bsg_misc/bsg_rotate_left.sv',
                    'external/basejump_stl/bsg_misc/bsg_rotate_right.sv',
                    'external/basejump_stl/bsg_misc/bsg_round_robin_arb.sv',
                    'external/basejump_stl/bsg_misc/bsg_scan.sv',
                    'external/basejump_stl/bsg_misc/bsg_strobe.sv',
                    'external/basejump_stl/bsg_misc/bsg_swap.sv',
                    'external/basejump_stl/bsg_misc/bsg_thermometer_count.sv',
                    'external/basejump_stl/bsg_misc/bsg_transpose.sv',
                    'external/basejump_stl/bsg_misc/bsg_unconcentrate_static.sv',
                    'external/basejump_stl/bsg_misc/bsg_xnor.sv',
                    'external/basejump_stl/bsg_noc/bsg_mesh_stitch.sv',
                    'external/basejump_stl/bsg_noc/bsg_noc_repeater_node.sv',
                    'external/basejump_stl/bsg_noc/bsg_wormhole_concentrator.sv',
                    'external/basejump_stl/bsg_noc/bsg_wormhole_concentrator_in.sv',
                    'external/basejump_stl/bsg_noc/bsg_wormhole_concentrator_out.sv',
                    'external/basejump_stl/bsg_noc/bsg_wormhole_router.sv',
                    'external/basejump_stl/bsg_noc/bsg_wormhole_router_adapter_in.sv',
                    'external/basejump_stl/bsg_noc/bsg_wormhole_router_adapter_out.sv',
                    'external/basejump_stl/bsg_noc/bsg_wormhole_router_decoder_dor.sv',
                    'external/basejump_stl/bsg_noc/bsg_wormhole_router_input_control.sv',
                    'external/basejump_stl/bsg_noc/bsg_wormhole_router_output_control.sv'])
                # BSG staging area, bsg modules that live in bp_common
                self.add_file([
                    'bp_common/src/v/bsg_async_noc_link.sv',
                    'bp_common/src/v/bsg_dff_sync_read.sv',
                    'bp_common/src/v/bsg_fifo_1r1w_edge.sv'])


class HardFloat(BlackParrotLibrary):
    """Berkeley HardFloat, the floating point units used by the back end."""

    def __init__(self):
        super().__init__("hardfloat")

        with self.active_fileset("rtl"):
            with self.active_dataroot("black-parrot"):
                self.add_idir([
                    'external/HardFloat/source',
                    'external/HardFloat/source/RISCV'])
                self.add_file([
                    'external/HardFloat/source/compareRecFN.v',
                    'external/HardFloat/source/divSqrtRecFN.v',
                    'external/HardFloat/source/divSqrtRecFN_medium.v',
                    'external/HardFloat/source/divSqrtRecFN_small.v',
                    'external/HardFloat/source/fNToRecFN.v',
                    'external/HardFloat/source/HardFloat_primitives.v',
                    'external/HardFloat/source/HardFloat_rawFN.v',
                    'external/HardFloat/source/iNToRecFN.v',
                    'external/HardFloat/source/isSigNaNRecFN.v',
                    'external/HardFloat/source/mulAddRecFN.v',
                    'external/HardFloat/source/mulRecFN.v',
                    'external/HardFloat/source/recFNToFN.v',
                    'external/HardFloat/source/recFNToIN.v',
                    'external/HardFloat/source/recFNToRecFN.v',
                    'external/HardFloat/source/RISCV/HardFloat_specialize.v'])


class BlackParrotCommon(BlackParrotLibrary):
    """Interface definitions, the configuration table, MMU, PMA and TLB."""

    def __init__(self):
        super().__init__("bp_common")

        with self.active_fileset("rtl"):
            self.add_depfileset(BaseJumpSTL(), "rtl")
            with self.active_dataroot("black-parrot"):
                self.add_idir('bp_common/src/include')
                # Packages
                self.add_file('bp_common/src/include/bp_common_pkg.sv')
                self.add_file([
                    'bp_common/src/v/bsg_bus_pack.sv',
                    'bp_common/src/v/bp_mmu.sv',
                    'bp_common/src/v/bp_pma.sv',
                    'bp_common/src/v/bp_tlb.sv'])


class BlackParrotFrontEnd(BlackParrotLibrary):
    """Front end: fetch, branch prediction and the I$."""

    def __init__(self):
        super().__init__("bp_fe")

        with self.active_fileset("rtl"):
            self.add_depfileset(BlackParrotCommon(), "rtl")
            with self.active_dataroot("black-parrot"):
                self.add_idir('bp_fe/src/include')
                # Packages
                self.add_file('bp_fe/src/include/bp_fe_pkg.sv')
                self.add_file([
                    'bp_fe/src/v/bp_fe_ras.sv',
                    'bp_fe/src/v/bp_fe_bht.sv',
                    'bp_fe/src/v/bp_fe_btb.sv',
                    'bp_fe/src/v/bp_fe_controller.sv',
                    'bp_fe/src/v/bp_fe_icache.sv',
                    'bp_fe/src/v/bp_fe_scan.sv',
                    'bp_fe/src/v/bp_fe_pc_gen.sv',
                    'bp_fe/src/v/bp_fe_realigner.sv',
                    'bp_fe/src/v/bp_fe_top.sv'])


class BlackParrotBackEnd(BlackParrotLibrary):
    """Back end: the calculator pipelines, checker, CSRs and the D$."""

    def __init__(self):
        super().__init__("bp_be")

        with self.active_fileset("rtl"):
            self.add_depfileset(BlackParrotCommon(), "rtl")
            self.add_depfileset(HardFloat(), "rtl")
            with self.active_dataroot("black-parrot"):
                self.add_idir('bp_be/src/include')
                # Packages
                self.add_file('bp_be/src/include/bp_be_pkg.sv')
                self.add_file('bp_be/src/v/bp_be_top.sv')
                # Calculator
                self.add_file([
                    'bp_be/src/v/bp_be_calculator/bp_be_calculator_top.sv',
                    'bp_be/src/v/bp_be_calculator/bp_be_csr.sv',
                    'bp_be/src/v/bp_be_calculator/bp_be_fp_box.sv',
                    'bp_be/src/v/bp_be_calculator/bp_be_fp_rebox.sv',
                    'bp_be/src/v/bp_be_calculator/bp_be_fp_unbox.sv',
                    'bp_be/src/v/bp_be_calculator/bp_be_int_unbox.sv',
                    'bp_be/src/v/bp_be_calculator/bp_be_int_box.sv',
                    'bp_be/src/v/bp_be_calculator/bp_be_pipe_int.sv',
                    'bp_be/src/v/bp_be_calculator/bp_be_pipe_aux.sv',
                    'bp_be/src/v/bp_be_calculator/bp_be_pipe_fma.sv',
                    'bp_be/src/v/bp_be_calculator/bp_be_pipe_long.sv',
                    'bp_be/src/v/bp_be_calculator/bp_be_pipe_mem.sv',
                    'bp_be/src/v/bp_be_calculator/bp_be_pipe_sys.sv',
                    'bp_be/src/v/bp_be_calculator/bp_be_ptw.sv',
                    'bp_be/src/v/bp_be_calculator/bp_be_rec_to_raw.sv',
                    'bp_be/src/v/bp_be_calculator/bp_be_reservation.sv'])
                # Checker
                self.add_file([
                    'bp_be/src/v/bp_be_checker/bp_be_cmd_queue.sv',
                    'bp_be/src/v/bp_be_checker/bp_be_detector.sv',
                    'bp_be/src/v/bp_be_checker/bp_be_director.sv',
                    'bp_be/src/v/bp_be_checker/bp_be_expander.sv',
                    'bp_be/src/v/bp_be_checker/bp_be_instr_decoder.sv',
                    'bp_be/src/v/bp_be_checker/bp_be_issue_queue.sv',
                    'bp_be/src/v/bp_be_checker/bp_be_regfile.sv',
                    'bp_be/src/v/bp_be_checker/bp_be_scheduler.sv',
                    'bp_be/src/v/bp_be_checker/bp_be_scoreboard.sv'])
                # D$
                self.add_file([
                    'bp_be/src/v/bp_be_dcache/bp_be_dcache.sv',
                    'bp_be/src/v/bp_be_dcache/bp_be_dcache_decoder.sv',
                    'bp_be/src/v/bp_be_dcache/bp_be_dcache_wbuf.sv'])


class BlackParrotMemoryEnd(BlackParrotLibrary):
    """Memory end: cache engines, coherence engine and the BedRock network."""

    def __init__(self):
        super().__init__("bp_me")

        with self.active_fileset("rtl"):
            self.add_depfileset(BlackParrotCommon(), "rtl")
            with self.active_dataroot("black-parrot"):
                self.add_idir('bp_me/src/include')
                # Packages
                self.add_file('bp_me/src/include/bp_me_pkg.sv')
                # LCE
                self.add_file([
                    'bp_me/src/v/lce/bp_lce.sv',
                    'bp_me/src/v/lce/bp_lce_req.sv',
                    'bp_me/src/v/lce/bp_lce_cmd.sv'])
                # Cache and devices
                self.add_file([
                    'bp_me/src/v/dev/bp_me_bedrock_register.sv',
                    'bp_me/src/v/dev/bp_me_cache_controller.sv',
                    'bp_me/src/v/dev/bp_me_dram_hash_decode.sv',
                    'bp_me/src/v/dev/bp_me_dram_hash_encode.sv',
                    'bp_me/src/v/dev/bp_me_cache_slice.sv',
                    'bp_me/src/v/dev/bp_me_cfg_slice.sv',
                    'bp_me/src/v/dev/bp_me_clint_slice.sv',
                    'bp_me/src/v/dev/bp_me_loopback.sv'])
                # CCE
                self.add_file([
                    'bp_me/src/v/cce/bp_cce.sv',
                    'bp_me/src/v/cce/bp_cce_alu.sv',
                    'bp_me/src/v/cce/bp_cce_arbitrate.sv',
                    'bp_me/src/v/cce/bp_cce_branch.sv',
                    'bp_me/src/v/cce/bp_cce_dir.sv',
                    'bp_me/src/v/cce/bp_cce_dir_lru_extract.sv',
                    'bp_me/src/v/cce/bp_cce_dir_segment.sv',
                    'bp_me/src/v/cce/bp_cce_dir_tag_checker.sv',
                    'bp_me/src/v/cce/bp_cce_gad.sv',
                    'bp_me/src/v/cce/bp_cce_inst_decode.sv',
                    'bp_me/src/v/cce/bp_cce_inst_predecode.sv',
                    'bp_me/src/v/cce/bp_cce_inst_ram.sv',
                    'bp_me/src/v/cce/bp_cce_inst_stall.sv',
                    'bp_me/src/v/cce/bp_cce_msg.sv',
                    'bp_me/src/v/cce/bp_cce_pending_bits.sv',
                    'bp_me/src/v/cce/bp_cce_pma.sv',
                    'bp_me/src/v/cce/bp_cce_reg.sv',
                    'bp_me/src/v/cce/bp_cce_spec_bits.sv',
                    'bp_me/src/v/cce/bp_cce_src_sel.sv',
                    'bp_me/src/v/cce/bp_io_cce.sv',
                    'bp_me/src/v/cce/bp_cce_fsm.sv',
                    'bp_me/src/v/cce/bp_cce_wrapper.sv'])
                # BedRock
                self.add_file('bp_me/src/v/cce/bp_bedrock_size_to_len.sv')
                # Network
                self.add_file([
                    'bp_me/src/v/cce/bp_uce.sv',
                    'bp_me/src/v/network/bp_me_addr_to_cce_id.sv',
                    'bp_me/src/v/network/bp_me_cce_id_to_cord.sv',
                    'bp_me/src/v/network/bp_me_cord_to_id.sv',
                    'bp_me/src/v/network/bp_me_lce_id_to_cord.sv',
                    'bp_me/src/v/network/bp_me_stream_pump.sv',
                    'bp_me/src/v/network/bp_me_stream_pump_in.sv',
                    'bp_me/src/v/network/bp_me_stream_pump_out.sv',
                    'bp_me/src/v/network/bp_me_stream_pump_control.sv',
                    'bp_me/src/v/network/bp_me_stream_to_wormhole.sv',
                    'bp_me/src/v/network/bp_me_wormhole_header_encode.sv',
                    'bp_me/src/v/network/bp_me_wormhole_to_stream.sv',
                    'bp_me/src/v/network/bp_me_wormhole_stream_control.sv',
                    'bp_me/src/v/network/bp_me_xbar_stream.sv',
                    'bp_me/src/v/network/bp_me_stream_gearbox.sv'])


class BlackParrotDesign(BlackParrotLibrary):
    def __init__(self):
        super().__init__("black_parrot")

        self.set_dataroot("extra", __file__)

        with self.active_fileset("rtl"):
            self.set_topmodule("bp_unicore_lite")
            # e_bp_unicore_tinyparrot_cfg does not elaborate: its single way
            # caches make the bp_uce way counter zero bits wide
            self.set_param("bp_params_p", "e_bp_unicore_miniparrot_cfg")
            self.add_define("SYNTHESIS")
            # basejump_stl assumes any synthesis tool it does not recognize is
            # vivado and emits an unsynthesizable module reference for the
            # memories, see BSG_VIVADO_SYNTH_FAILS in bsg_defines.sv
            self.add_define("YOSYS")

            self.add_depfileset(BlackParrotFrontEnd(), "rtl")
            self.add_depfileset(BlackParrotBackEnd(), "rtl")
            self.add_depfileset(BlackParrotMemoryEnd(), "rtl")

            with self.active_dataroot("black-parrot"):
                self.add_idir('bp_top/src/include')
                # Packages
                self.add_file('bp_top/src/include/bp_top_pkg.sv')
                self.add_file([
                    'bp_top/src/v/bp_nd_socket.sv',
                    'bp_top/src/v/bp_cacc_vdp.sv',
                    'bp_top/src/v/bp_cacc_tile.sv',
                    'bp_top/src/v/bp_cacc_tile_node.sv',
                    'bp_top/src/v/bp_cacc_complex.sv',
                    'bp_top/src/v/bp_sacc_vdp.sv',
                    'bp_top/src/v/bp_sacc_scratchpad.sv',
                    'bp_top/src/v/bp_sacc_tile.sv',
                    'bp_top/src/v/bp_sacc_tile_node.sv',
                    'bp_top/src/v/bp_sacc_complex.sv',
                    'bp_top/src/v/bp_core.sv',
                    'bp_top/src/v/bp_core_lite.sv',
                    'bp_top/src/v/bp_core_minimal.sv',
                    'bp_top/src/v/bp_core_complex.sv',
                    'bp_top/src/v/bp_l2e_tile.sv',
                    'bp_top/src/v/bp_l2e_tile_node.sv',
                    'bp_top/src/v/bp_io_complex.sv',
                    'bp_top/src/v/bp_io_link_to_lce.sv',
                    'bp_top/src/v/bp_io_tile.sv',
                    'bp_top/src/v/bp_io_tile_node.sv',
                    'bp_top/src/v/bp_mem_complex.sv',
                    'bp_top/src/v/bp_multicore.sv',
                    'bp_top/src/v/bp_unicore.sv',
                    'bp_top/src/v/bp_unicore_lite.sv',
                    'bp_top/src/v/bp_core_tile.sv',
                    'bp_top/src/v/bp_core_tile_node.sv',
                    'bp_top/src/v/bp_processor.sv'])

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

    def setup_freepdk45(self, project: ASIC):
        ASICSynthesis.find_task(project).set_yosys_useslang(True)
        ASICSynthesis.find_task(project).set_yosys_strategy('AREA3')
        ASICSynthesis.find_task(project).set_yosys_flatten(False)
        ASICSynthesis.find_task(project).set_yosys_abcclockderating(0.95)

    def setup_asap7(self, project: ASIC):
        ASICSynthesis.find_task(project).set_yosys_useslang(True)
        ASICSynthesis.find_task(project).set_yosys_strategy('AREA3')
        ASICSynthesis.find_task(project).set_yosys_flatten(False)
        ASICSynthesis.find_task(project).set_yosys_abcclockderating(0.95)

    def setup_ihp130(self, project: ASIC):
        ASICSynthesis.find_task(project).set_yosys_useslang(True)
        ASICSynthesis.find_task(project).set_yosys_strategy('AREA3')
        ASICSynthesis.find_task(project).set_yosys_flatten(False)
        ASICSynthesis.find_task(project).set_yosys_abcclockderating(0.95)

    def setup_gf180(self, project: ASIC):
        ASICSynthesis.find_task(project).set_yosys_useslang(True)
        ASICSynthesis.find_task(project).set_yosys_strategy('AREA3')
        ASICSynthesis.find_task(project).set_yosys_flatten(False)
        ASICSynthesis.find_task(project).set_yosys_abcclockderating(0.95)

    def setup_skywater130(self, project: ASIC):
        ASICSynthesis.find_task(project).set_yosys_useslang(True)
        ASICSynthesis.find_task(project).set_yosys_flatten(False)
        ASICSynthesis.find_task(project).set_yosys_abcclockderating(0.95)


if __name__ == '__main__':
    project = ASIC(BlackParrotDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    asap7_demo(project)
    project.design.process_setups("asap7_asap7sc7p5t_rvt", project)

    project.run()
    project.summary()
