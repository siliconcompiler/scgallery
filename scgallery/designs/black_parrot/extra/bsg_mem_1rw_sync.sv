//
// Replacement for external/basejump_stl/bsg_mem/bsg_mem_1rw_sync.sv
//
// Memories large enough to be worth hardening are mapped onto la_spram,
// everything else uses the basejump_stl behavioral model so it synthesizes
// into flops instead of a tiny macro.
//

`include "bsg_defines.sv"

module bsg_mem_1rw_sync #(parameter `BSG_INV_PARAM(width_p)
                          , parameter `BSG_INV_PARAM(els_p)
                          , parameter latch_last_read_p=0
                          , parameter addr_width_lp=`BSG_SAFE_CLOG2(els_p)
                          , parameter enable_clock_gating_p=0
                          , parameter verbose_if_synth_p=1
                          , parameter harden_bits_p=4096
                          )
   (input   clk_i
    , input reset_i
    , input [`BSG_SAFE_MINUS(width_p, 1):0] data_i
    , input [addr_width_lp-1:0] addr_i
    , input v_i
    , input w_i
    , output logic [`BSG_SAFE_MINUS(width_p, 1):0]  data_o
    );

   if ((width_p * els_p) >= harden_bits_p)
     begin : macro
       la_spram
        #(.DW(width_p)
          ,.AW(addr_width_lp)
          ,.BYTEMASK(0)
          ) mem
         (.clk(clk_i)
          ,.ce(v_i)
          ,.we(v_i & w_i)
          ,.wmask({width_p{1'b1}})
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
       bsg_mem_1rw_sync_synth
        #(.width_p(width_p)
          ,.els_p(els_p)
          ,.latch_last_read_p(latch_last_read_p)
          ,.verbose_p(verbose_if_synth_p)
          ) synth
         (.clk_i(clk_i)
          ,.reset_i(reset_i)
          ,.data_i(data_i)
          ,.addr_i(addr_i)
          ,.v_i(v_i)
          ,.w_i(w_i)
          ,.data_o(data_o)
          );
     end

endmodule

`BSG_ABSTRACT_MODULE(bsg_mem_1rw_sync)
