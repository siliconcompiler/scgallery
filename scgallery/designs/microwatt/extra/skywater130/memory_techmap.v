module $_SKY130_SRAM_1R1W_ 
#(
    parameter PORT_A_WIDTH = 64,
    parameter PORT_A_WR_EN_WIDTH = 8,
    parameter PORT_B_WIDTH = 64
)
(
    input [7:0] PORT_A_ADDR,
    input PORT_A_CLK,
    output [PORT_A_WIDTH-1:0] PORT_A_RD_DATA,
    input PORT_A_RD_EN,
    input [PORT_A_WIDTH-1:0] PORT_A_WR_DATA,
    input [PORT_A_WR_EN_WIDTH-1:0] PORT_A_WR_EN,

    input PORT_B_CLK,
    input PORT_B_RD_EN,
    input [7:0] PORT_B_ADDR,
    output [PORT_B_WIDTH-1:0] PORT_B_RD_DATA
);

sky130_sram_1rw1r_64x256_8 _TECHMAP_REPLACE_ (
    .clk0(PORT_A_CLK),
    .csb0(~(|PORT_A_WR_EN || PORT_A_RD_EN)),
    .web0(~(|PORT_A_WR_EN)),
    .wmask0(PORT_A_WR_EN),
    .din0(PORT_A_WR_DATA),
    .dout0(PORT_A_RD_DATA),
    .addr0(PORT_A_ADDR),

    .clk1(PORT_B_CLK),
    .addr1(PORT_B_ADDR),
    .csb1(~PORT_B_RD_EN),
    .dout1(PORT_B_RD_DATA));

endmodule
