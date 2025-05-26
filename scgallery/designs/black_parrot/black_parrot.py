#!/usr/bin/env python3

'''
BlackParrot: A Linux-Capable Accelerator Host RISC-V Multicore

BlackParrot aims to be the default open-source, Linux-capable, cache-coherent,
RV64GC multicore used by the world. Although originally developed by the
University of Washington and Boston University, BlackParrot strives to be
community-driven and infrastructure agnostic, a core which is Pareto optimal
in terms of power, performance, area and complexity. In order to ensure BlackParrot
is easy to use, integrate, modify and trust, development is guided by three core
principles: Be Tiny, Be Modular, and Be Friendly. Development efforts have prioritized
ease of use and silicon validation as first order design metrics, so that users can
quickly get started and trust that their results will be representative of
state-of-the-art ASIC designs. BlackParrot is ideal as the basis for a lightweight
accelerator host, a standalone Linux core, or as a hardware research platform.

Source: https://github.com/black-parrot/black-parrot
'''

import os

from siliconcompiler import Chip
from siliconcompiler.targets import freepdk45_demo
from scgallery import Gallery
from lambdalib import ramlib

from siliconcompiler.tools import openroad
from siliconcompiler.tools._common import get_tool_tasks


def setup():
    chip = Chip('black_parrot')

    chip.set('option', 'entrypoint', 'bp_multicore')

    chip.register_source('blackparrot',
                         path='git+https://github.com/black-parrot/black-parrot.git',
                         ref='ea328c9dcf918825e9c92353b00d32df24a63415')

    extra_root = os.path.join('black_parrot', 'extra')

    for src in (
            'external/basejump_stl/bsg_axi/bsg_axi_pkg.sv',
            'external/basejump_stl/bsg_cache/bsg_cache_pkg.sv',
            'external/basejump_stl/bsg_noc/bsg_noc_pkg.sv',
            'external/basejump_stl/bsg_noc/bsg_wormhole_router_pkg.sv',
            'bp_common/src/include/bp_common_pkg.sv',
            'bp_fe/src/include/bp_fe_pkg.sv',
            'bp_be/src/include/bp_be_pkg.sv',
            'bp_me/src/include/bp_me_pkg.sv',
            'bp_top/src/include/bp_top_pkg.sv',
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
            'external/basejump_stl/bsg_dataflow/bsg_fifo_1rw_large.sv',
            'external/basejump_stl/bsg_dataflow/bsg_fifo_tracker.sv',
            'external/basejump_stl/bsg_dataflow/bsg_flow_counter.sv',
            'external/basejump_stl/bsg_dataflow/bsg_one_fifo.sv',
            'external/basejump_stl/bsg_dataflow/bsg_parallel_in_serial_out.sv',
            'external/basejump_stl/bsg_dataflow/bsg_parallel_in_serial_out_dynamic.sv',
            'external/basejump_stl/bsg_dataflow/bsg_parallel_in_serial_out_passthrough.sv',
            'bp_common/src/v/bsg_parallel_in_serial_out_passthrough_dynamic.v',
            'bp_common/src/v/bsg_serial_in_parallel_out_passthrough_dynamic.v',
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
            'external/basejump_stl/bsg_noc/bsg_wormhole_router_output_control.sv',
            'external/HardFloat/source/addRecFN.v',
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
            'external/HardFloat/source/RISCV/HardFloat_specialize.v',
            'bp_common/src/v/bsg_fifo_1r1w_rolly.sv',
            'bp_common/src/v/bsg_bus_pack.sv',
            'bp_common/src/v/bp_mmu.sv',
            'bp_common/src/v/bp_pma.sv',
            'bp_common/src/v/bp_tlb.sv',
            'bp_be/src/v/bp_be_top.sv',
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
            'bp_be/src/v/bp_be_calculator/bp_be_reservation.sv',
            'bp_be/src/v/bp_be_checker/bp_be_cmd_queue.sv',
            'bp_be/src/v/bp_be_checker/bp_be_detector.sv',
            'bp_be/src/v/bp_be_checker/bp_be_director.sv',
            'bp_be/src/v/bp_be_checker/bp_be_expander.sv',
            'bp_be/src/v/bp_be_checker/bp_be_instr_decoder.sv',
            'bp_be/src/v/bp_be_checker/bp_be_issue_queue.sv',
            'bp_be/src/v/bp_be_checker/bp_be_regfile.sv',
            'bp_be/src/v/bp_be_checker/bp_be_scheduler.sv',
            'bp_be/src/v/bp_be_checker/bp_be_scoreboard.sv',
            'bp_be/src/v/bp_be_dcache/bp_be_dcache.sv',
            'bp_be/src/v/bp_be_dcache/bp_be_dcache_decoder.sv',
            'bp_be/src/v/bp_be_dcache/bp_be_dcache_wbuf.sv',
            'bp_fe/src/v/bp_fe_ras.sv',
            'bp_fe/src/v/bp_fe_bht.sv',
            'bp_fe/src/v/bp_fe_btb.sv',
            'bp_fe/src/v/bp_fe_controller.sv',
            'bp_fe/src/v/bp_fe_icache.sv',
            'bp_fe/src/v/bp_fe_instr_scan.sv',
            'bp_fe/src/v/bp_fe_pc_gen.sv',
            'bp_fe/src/v/bp_fe_realigner.sv',
            'bp_fe/src/v/bp_fe_top.sv',
            'bp_me/src/v/lce/bp_lce.sv',
            'bp_me/src/v/lce/bp_lce_req.sv',
            'bp_me/src/v/lce/bp_lce_cmd.sv',
            'bp_me/src/v/dev/bp_me_bedrock_register.sv',
            'bp_me/src/v/dev/bp_me_cache_controller.sv',
            'bp_me/src/v/dev/bp_me_dram_hash_decode.sv',
            'bp_me/src/v/dev/bp_me_dram_hash_encode.sv',
            'bp_me/src/v/dev/bp_me_cache_slice.sv',
            'bp_me/src/v/dev/bp_me_cfg_slice.sv',
            'bp_me/src/v/dev/bp_me_clint_slice.sv',
            'bp_me/src/v/dev/bp_me_loopback.sv',
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
            'bp_me/src/v/cce/bp_cce_wrapper.sv',
            'bp_me/src/v/cce/bp_bedrock_size_to_len.sv',
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
            'bp_me/src/v/network/bp_me_stream_gearbox.sv',
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
            'bp_top/src/v/bp_processor.sv',
            'bp_common/src/v/bsg_async_noc_link.sv',
            'bp_common/src/v/bsg_dff_sync_read.v',
            'bp_common/src/v/bsg_rom_param.v'):
        chip.input(src, package='blackparrot')

    chip.add('option', 'idir', 'external/basejump_stl/bsg_misc', package='blackparrot')
    chip.add('option', 'idir', 'bp_common/src/include', package='blackparrot')
    chip.add('option', 'idir', 'bp_me/src/include', package='blackparrot')
    chip.add('option', 'idir', 'bp_be/src/include', package='blackparrot')
    chip.add('option', 'idir', 'bp_fe/src/include', package='blackparrot')
    chip.add('option', 'idir', 'bp_top/src/include', package='blackparrot')
    chip.add('option', 'idir', 'external/basejump_stl/bsg_cache', package='blackparrot')
    chip.add('option', 'idir', 'external/basejump_stl/bsg_noc', package='blackparrot')
    chip.add('option', 'idir', 'external/HardFloat/source/RISCV', package='blackparrot')
    chip.add('option', 'idir', 'external/HardFloat/source', package='blackparrot')

    chip.input('black_parrot/extra/bsg_mem_1rw_sync.sv',
               package='scgallery-designs')
    chip.input('black_parrot/extra/bsg_mem_1rw_sync_mask_write_byte.sv',
               package='scgallery-designs')
    chip.input('black_parrot/extra/bsg_mem_1rw_sync_mask_write_bit.sv',
               package='scgallery-designs')
    chip.use(ramlib)

    return chip


def setup_physical(chip):
    chip.set('option', 'define', 'SYNTHESIS')
    chip.add('option', 'define', 'VERILATOR')

    chip.set('tool', 'sv2v', 'task', 'convert', 'var', 'skip_convert', True)
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'use_slang', True)

    if chip.get('option', 'pdk') == 'skywater130':
        pass
    else:
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'strategy', 'AREA3')

    for task in get_tool_tasks(chip, openroad):
        chip.set('tool', 'openroad', 'task', task, 'var', 'sta_define_path_groups', False)

    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'flatten', 'false')
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'abc_clock_derating', '0.95')


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=freepdk45_demo, module_path=__file__)
    setup_physical(chip)

    chip.run()
    chip.summary()
