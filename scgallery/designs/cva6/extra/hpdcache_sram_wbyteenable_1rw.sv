module hpdcache_sram_wbyteenable_1rw
#(
    parameter int unsigned ADDR_SIZE = 0,
    parameter int unsigned DATA_SIZE = 0,
    parameter int unsigned DEPTH = 2**ADDR_SIZE
)
(
    input  logic                   clk,
    input  logic                   rst_n,
    input  logic                   cs,
    input  logic                   we,
    input  logic [ADDR_SIZE-1:0]   addr,
    input  logic [DATA_SIZE-1:0]   wdata,
    input  logic [DATA_SIZE/8-1:0] wbyteenable,
    output logic [DATA_SIZE-1:0]   rdata
);
    logic [DATA_SIZE-1:0] wmask;

    genvar i;
    genvar j;
    generate
        for ( i = 0; i < DATA_SIZE/8; i++) begin
            for ( j = 0; j < 8; j++) begin
                assign wmask[i*8 + j] = wbyteenable[i];
            end
        end
    endgenerate

    la_spram #(.DW(DATA_SIZE), .AW(ADDR_SIZE)) mem (
        .clk(clk),
        .ce(cs),
        .we(we),
        .wmask(wmask),
        .addr(addr),
        .din(wdata),
        .dout(rdata),
        .ctrl(),
        .test(),
        .vss(),
        .vdd(),
        .vddio()
    );

endmodule : hpdcache_sram_wbyteenable_1rw
