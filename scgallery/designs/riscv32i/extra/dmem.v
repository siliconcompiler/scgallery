//------------------------------------------------
// dmem.v
// James E. Stine
// February 1, 2018
// Oklahoma State University
// ECEN 4243
// Harvard Architecture Data Memory (Big Endian)
//------------------------------------------------

module dmem (clk, r_w, mem_addr, mem_data, mem_out);

   input         clk;
   input         r_w;
   input [31:0]  mem_addr;
   input [31:0]  mem_data;
   output reg [31:0] mem_out;
   wire [1:0]    sel_mem;
   wire [3:0]    ce_mem;
   reg  [3:0]    we_mem;

   wire [31:0] inter_dmem0;
   wire [31:0] inter_dmem1;
   wire [31:0] inter_dmem2;
   wire [31:0] inter_dmem3;

   assign ce_mem = (mem_addr[31] == 1) ? 4'b1000 :
                   (mem_addr[23] == 1) ? 4'b0100 :
                   (mem_addr[15] == 1) ? 4'b0010 :
                   4'b0001;

   always @* begin
      if (!r_w) begin
         we_mem = 4'b0000;
      end else if (mem_addr[31]) begin
         we_mem = 4'b1000;
      end else if (mem_addr[23]) begin
         we_mem = 4'b0100;
      end else if (mem_addr[15]) begin
         we_mem = 4'b0010;
      end else begin
         we_mem = 4'b0001;
      end
   end // always @ *

   la_spram #(.DW(32), .AW(8)) dmem0(.clk(clk), .ce(ce_mem[0]), .we(we_mem[0]), .wmask(32'hffffffff), .addr(mem_addr[7:0]), .din(mem_data), .dout(inter_dmem0), .ctrl(), .test(), .vss(), .vdd(), .vddio());
   la_spram #(.DW(32), .AW(8)) dmem1(.clk(clk), .ce(ce_mem[1]), .we(we_mem[1]), .wmask(32'hffffffff), .addr(mem_addr[15:8]), .din(mem_data), .dout(inter_dmem1), .ctrl(), .test(), .vss(), .vdd(), .vddio());
   la_spram #(.DW(32), .AW(8)) dmem2(.clk(clk), .ce(ce_mem[2]), .we(we_mem[2]), .wmask(32'hffffffff), .addr(mem_addr[23:16]), .din(mem_data), .dout(inter_dmem2), .ctrl(), .test(), .vss(), .vdd(), .vddio());
   la_spram #(.DW(32), .AW(8)) dmem3(.clk(clk), .ce(ce_mem[3]), .we(we_mem[3]), .wmask(32'hffffffff), .addr(mem_addr[31:24]), .din(mem_data), .dout(inter_dmem3), .ctrl(), .test(), .vss(), .vdd(), .vddio());

   assign sel_mem = (mem_addr[31] == 1) ? 2'b11 :
                    (mem_addr[23] == 1) ? 2'b10 :
                    (mem_addr[15] == 1) ? 2'b01 :
                    2'b00;

   always @* begin
      case (sel_mem)
        2'b00: mem_out = inter_dmem0;
        2'b01: mem_out = inter_dmem1;
        2'b10: mem_out = inter_dmem2;
        2'b11: mem_out = inter_dmem3;
      endcase // case (sel_mem)
   end

endmodule // mem
