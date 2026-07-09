module Sram_512x128(
  input          clock,
  input          enable,
  input          write,
  input  [8:0]   addr,
  input  [127:0] wdata,
  input  [15:0] wmask,
  output [127:0] rdata
);

  la_spram #(.DW(128), .AW(9), .BYTEMASK(1)) memory (
    .clk(clock),
    .ce(enable),
    .we(write),
    .wmask(wmask),
    .addr(addr),
    .din(wdata),
    .dout(rdata),
    .selctrl(1'b0),
    .ctrl('b0),
    .status()
  );

endmodule

module Sram_2048x128(
  input          clock,
  input          enable,
  input          write,
  input  [10:0]   addr,
  input  [127:0] wdata,
  input  [15:0] wmask,
  output [127:0] rdata
);

  la_spram #(.DW(128), .AW(11), .BYTEMASK(1)) memory (
    .clk(clock),
    .ce(enable),
    .we(write),
    .wmask(wmask),
    .addr(addr),
    .din(wdata),
    .dout(rdata),
    .selctrl(1'b0),
    .ctrl('b0),
    .status()
  );

endmodule
