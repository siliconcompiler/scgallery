//
// Replacement for the Sram module shipped in the CoralNPU release bundle
// (Sram.v), which selects between vendor macros and a behavioral model with
// `ifdef USE_TSMC12FFC / USE_GF22. This maps it onto la_spram instead, so the
// TCMs become SRAM macros for whichever PDK is being targeted.
//
// GLOBAL_BASE_ADDR is only used by the simulation backdoor in the upstream
// model and has no effect on the hardware, it is kept for interface
// compatibility.
//

module Sram #(
    parameter NUM_ENTRIES = 128,
    parameter GLOBAL_BASE_ADDR = 0
) (
    input                            clock,
    input                            enable,
    input                            write,
    input  [$clog2(NUM_ENTRIES)-1:0] addr,
    input  [                  127:0] wdata,
    input  [                   15:0] wmask,
    output [                  127:0] rdata,
    output                           rvalid
);

  // The upstream model returns read data one cycle after enable
  reg rvalid_reg;
  always @(posedge clock) rvalid_reg <= enable;
  assign rvalid = rvalid_reg;

  la_spram #(
      .DW(128),
      .AW($clog2(NUM_ENTRIES)),
      .BYTEMASK(1)
  ) memory (
      .clk(clock),
      .ce(enable),
      .we(enable & write),
      .wmask(wmask),
      .addr(addr),
      .din(wdata),
      .dout(rdata),
      .selctrl(1'b0),
      .ctrl('b0),
      .status()
  );

endmodule
