//
// Synchronous 1-port ram.
// Only one read or one write may be done per cycle.

`include "bsg_defines.sv"

module bsg_mem_1rw_sync_mask_write_bit #(
  parameter `BSG_INV_PARAM(width_p)
  , parameter `BSG_INV_PARAM(els_p)
  , parameter latch_last_read_p=0
  , parameter enable_clock_gating_p=0
  , parameter addr_width_lp=`BSG_SAFE_CLOG2(els_p)
) (input   clk_i
    , input reset_i
    , input [`BSG_SAFE_MINUS(width_p, 1):0] data_i
    , input [addr_width_lp-1:0] addr_i
    , input v_i
    , input [`BSG_SAFE_MINUS(width_p, 1):0] w_mask_i
    , input w_i
    , output [`BSG_SAFE_MINUS(width_p, 1):0]  data_o
);

   wire clk_lo;

   if (enable_clock_gating_p)
     begin
       bsg_clkgate_optional icg
         (.clk_i( clk_i )
         ,.en_i( v_i )
         ,.bypass_i( 1'b0 )
         ,.gated_clock_o( clk_lo )
         );
     end
   else
     begin
       assign clk_lo = clk_i;
     end


  la_spram #(.DW(width_p), .AW(addr_width_lp)) mem(
    .clk(clk_lo),
    .ce(v_i),
    .we(w_i),
    .wmask(w_mask_i),
    .addr(addr_i),
    .din(data_i),
    .dout(data_o),
    .ctrl(),
    .test(),
    .vdd(),
    .vss(),
    .vddio()
  );

endmodule
