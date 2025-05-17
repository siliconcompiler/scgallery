// Copyright (c) 2023 - 2024 Meinhard Kissich
// SPDX-License-Identifier: MIT
// -----------------------------------------------------------------------------
// File  :  fazyrv_ram_sp.v
// Usage :  General purpose RAM used in FazyRV SoCs.
//
// Param
//  - REGW        Width of registers.
//  - ADRW        Width of address.
//  - DEPTH       Depth of memory.
//
// Ports
//  - clk_i       Clock input, sensitive to rising edge.
//  - we_i        Write enable.
//  - waddr_i     Write address.
//  - raddr_i     Read address.
//  - wdata_i     Write data.
//  - rdata_o     Read data.
// -----------------------------------------------------------------------------

module fazyrv_ram_sp #( parameter REGW=32, parameter ADRW=5, parameter DEPTH=32 ) (
  input  logic            clk_i,
  input  logic            we_i,
  input  logic [ADRW-1:0] waddr_i,
  input  logic [ADRW-1:0] raddr_i,
  input  logic [REGW-1:0] wdata_i,
  output logic [REGW-1:0] rdata_o
);

la_spram #(
        .DW(REGW),
        .AW(ADRW)
    ) ram (
        .clk(clk_i),
        .ce('b1),
        .we(we_i),
        .wmask({REGW{1'b1}}),
        .addr(we_i ? waddr_i : raddr_i),
        .din(wdata_i),
        .dout(rdata_o)
    );

endmodule
