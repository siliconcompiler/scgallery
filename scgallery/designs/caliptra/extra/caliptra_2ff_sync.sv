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

module caliptra_2ff_sync  #( parameter WIDTH=1,
                             parameter RST_VAL=0)
    (
    input logic clk,
    input logic rst_b,
    input logic [WIDTH-1:0] din,
    output logic [WIDTH-1:0] dout

);

   genvar i;
   generate
      for (i = 0; i < WIDTH; i++) begin : sync_bits
         la_drsync #(
            .STAGES(2)
         ) sync (
            .clk(clk),
            .nreset(rst_b),
            .in(din[i]),
            .out(dout[i])
         );
      end
   endgenerate

endmodule
