`include "bsg_defines.sv"

module bsg_mem_1rw_sync_mask_write_byte #(parameter `BSG_INV_PARAM(els_p)
                                          ,parameter addr_width_lp = `BSG_SAFE_CLOG2(els_p)

                                          ,parameter `BSG_INV_PARAM(data_width_p )
                                          ,parameter latch_last_read_p=0
                                          ,parameter write_mask_width_lp = data_width_p>>3
                                          ,parameter enable_clock_gating_p=0
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

    logic [`BSG_SAFE_MINUS(data_width_p, 1):0] wmask;

    genvar i;
    genvar j;
    generate
        for ( i = 0; i < write_mask_width_lp; i++) begin
            for ( j = 0; j < 8; j++) begin
                assign wmask[i*8 + j] = write_mask_i[i];
            end
        end
    endgenerate

  la_spram #(.DW(data_width_p), .AW(addr_width_lp)) mem(
    .clk(clk_lo),
    .ce(v_i),
    .we(w_i),
    .wmask(wmask),
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
