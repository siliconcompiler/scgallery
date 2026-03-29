module hpdcache_sram_1rw
#(
    parameter int unsigned ADDR_SIZE = 0,
    parameter int unsigned DATA_SIZE = 0,
    parameter int unsigned DEPTH = 2**ADDR_SIZE
)
(
    input  logic                  clk,
    input  logic                  rst_n,
    input  logic                  cs,
    input  logic                  we,
    input  logic [ADDR_SIZE-1:0]  addr,
    input  logic [DATA_SIZE-1:0]  wdata,
    output logic [DATA_SIZE-1:0]  rdata
);

    la_spram #(.DW(DATA_SIZE), .AW(ADDR_SIZE)) mem (
        .clk(clk),
        .ce(cs),
        .we(we),
        .wmask({DATA_SIZE{1'b1}}),
        .addr(addr),
        .din(wdata),
        .dout(rdata),
        .selctrl(1'b0),
        .ctrl('b0),
        .status()
    );

endmodule : hpdcache_sram_1rw
