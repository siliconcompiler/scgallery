// SPDX-License-Identifier: Apache-2.0
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module caliptra_sram #(
     parameter DEPTH      = 64
    ,parameter DATA_WIDTH = 32
    ,parameter ADDR_WIDTH = $clog2(DEPTH)

    )
    (
    input  logic                       clk_i,

    input  logic                       cs_i,
    input  logic                       we_i,
    input  logic [ADDR_WIDTH-1:0]      addr_i,
    input  logic [DATA_WIDTH-1:0]      wdata_i,
    output logic [DATA_WIDTH-1:0]      rdata_o
    );

   la_spram #(
      .DW(DATA_WIDTH),
      .AW(ADDR_WIDTH)
   ) ram (
      .clk(clk_i),
      .ce(cs_i),
      .we(we_i),
      .wmask({DATA_WIDTH{1'b1}}),
      .addr(addr_i),
      .din(wdata_i),
      .dout(rdata_o),
      .selctrl(1'b0),
      .ctrl('b0),
      .status()
   );

endmodule
