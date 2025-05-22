// Copyright 2018 ETH Zurich and University of Bologna.
// Copyright and related rights are licensed under the Solderpad Hardware
// License, Version 0.51 (the "License"); you may not use this file except in
// compliance with the License.  You may obtain a copy of the License at
// http://solderpad.org/licenses/SHL-0.51. Unless required by applicable law
// or agreed to in writing, software, hardware and materials distributed under
// this License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
// CONDITIONS OF ANY KIND, either express or implied. See the License for the
// specific language governing permissions and limitations under the License.
//
// Author: Florian Zaruba    <zarubaf@iis.ee.ethz.ch>, ETH Zurich
//         Michael Schaffner <schaffner@iis.ee.ethz.ch>, ETH Zurich
// Date: 15.08.2018
// Description: SRAM wrapper for FPGA (requires the fpga-support submodule)
//
// Note: the wrapped module contains two different implementations for
// ALTERA and XILINX tools, since these follow different coding styles for
// inferrable RAMS with byte enable. define `FPGA_TARGET_XILINX or
// `FPGA_TARGET_ALTERA in your build environment (default is ALTERA)

module sram_cache #(
    parameter DATA_WIDTH = 64,
    parameter USER_WIDTH = 1,
    parameter USER_EN    = 0,
    parameter NUM_WORDS  = 1024,
    parameter SIM_INIT   = "none",
    parameter BYTE_ACCESS = 1,
    parameter TECHNO_CUT = 0,
    parameter OUT_REGS   = 0     // enables output registers in FPGA macro (read lat = 2)
)(
   input  logic                          clk_i,
   input  logic                          rst_ni,
   input  logic                          req_i,
   input  logic                          we_i,
   input  logic [$clog2(NUM_WORDS)-1:0]  addr_i,
   input  logic [USER_WIDTH-1:0]         wuser_i,
   input  logic [DATA_WIDTH-1:0]         wdata_i,
   input  logic [(DATA_WIDTH+7)/8-1:0]   be_i,
   output logic [USER_WIDTH-1:0]         ruser_o,
   output logic [DATA_WIDTH-1:0]         rdata_o
);
  localparam DATA_AND_USER_WIDTH = USER_EN ? DATA_WIDTH + USER_WIDTH : DATA_WIDTH;

  logic [DATA_WIDTH-1:0] wdata_user;
  logic [DATA_WIDTH-1:0] rdata_user;
  logic [(DATA_WIDTH+7)/8-1:0] be;

  always_comb begin
    wdata_user = wdata_i;
    be         = be_i;
    rdata_o    = rdata_user;
    ruser_o    = '0;
  end

  logic [DATA_AND_USER_WIDTH-1:0] wmask;

  genvar i;
  genvar j;
  generate
      for ( i = 0; i < DATA_WIDTH/8; i++) begin
          for ( j = 0; j < 8; j++) begin
              assign wmask[i*8 + j] = be[i];
          end
      end
  endgenerate

  la_spram #(.DW(DATA_AND_USER_WIDTH), .AW($clog2(NUM_WORDS))) i_tc_sram_wrapper (
    .clk(clk_i),
    .ce(req_i),
    .we(we_i),
    .wmask(wmask),
    .addr(addr_i),
    .din(wdata_user),
    .dout(rdata_user),
    .ctrl(),
    .test(),
    .vss(),
    .vdd(),
    .vddio()
  );

endmodule : sram_cache
