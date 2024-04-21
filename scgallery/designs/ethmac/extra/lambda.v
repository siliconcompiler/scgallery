module vs_hdsp_256x32_bw(
  input CK,
  input CEN,
  input WEN,
  input OEN,
  input [7:0] ADR,
  input [31:0] DI,
  output [31:0] DOUT
);

  la_spram #(.DW(32), .AW(8)) mem (
    .clk(CK),
    .dout(DOUT),
    .ce(~CEN),
    .we(~OEN),
    .wmask({32{1'b1}}),
    .addr(ADR),
    .din(DI)
  );

endmodule
