//
// Replacement for
// external/basejump_stl/bsg_mem/bsg_mem_1rw_sync_mask_write_byte.sv
//
// Memories large enough to be worth hardening are mapped onto la_spram,
// everything else uses the basejump_stl behavioral model so it synthesizes
// into flops instead of a tiny macro.
//

`include "bsg_defines.sv"

module bsg_mem_1rw_sync_mask_write_byte #(parameter `BSG_INV_PARAM(els_p)
                                          ,parameter addr_width_lp = `BSG_SAFE_CLOG2(els_p)

                                          ,parameter `BSG_INV_PARAM(data_width_p )
                                          ,parameter latch_last_read_p=0
                                          ,parameter write_mask_width_lp = data_width_p>>3
                                          ,parameter enable_clock_gating_p=0
                                          ,parameter harden_bits_p=4096
                                         )
  ( input clk_i
   ,input reset_i

   ,input v_i
   ,input w_i

   ,input [addr_width_lp-1:0]       addr_i
   ,input [`BSG_SAFE_MINUS(data_width_p, 1):0]        data_i
    // for each bit set in the mask, a byte is written
   ,input [`BSG_SAFE_MINUS(write_mask_width_lp, 1):0] write_mask_i

   ,output logic [`BSG_SAFE_MINUS(data_width_p, 1):0] data_o
  );

   if (((data_width_p * els_p) >= harden_bits_p) && ((data_width_p % 8) == 0))
     begin : macro
       la_spram
        #(.DW(data_width_p)
          ,.AW(addr_width_lp)
          ,.BYTEMASK(1)
          ) mem
         (.clk(clk_i)
          ,.ce(v_i)
          ,.we(v_i & w_i)
          ,.wmask(write_mask_i)
          ,.addr(addr_i)
          ,.din(data_i)
          ,.dout(data_o)
          ,.selctrl(1'b0)
          ,.ctrl('0)
          ,.status()
          );
     end
   else
     begin : synth
       bsg_mem_1rw_sync_mask_write_byte_synth
        #(.els_p(els_p)
          ,.data_width_p(data_width_p)
          ,.latch_last_read_p(latch_last_read_p)
          ) synth
         (.clk_i(clk_i)
          ,.reset_i(reset_i)
          ,.v_i(v_i)
          ,.w_i(w_i)
          ,.addr_i(addr_i)
          ,.data_i(data_i)
          ,.write_mask_i(write_mask_i)
          ,.data_o(data_o)
          );
     end

endmodule

`BSG_ABSTRACT_MODULE(bsg_mem_1rw_sync_mask_write_byte)
