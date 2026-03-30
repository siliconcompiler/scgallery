//------------------------------------------------
// dmem.v
// James E. Stine
// February 1, 2018
// Oklahoma State University
// ECEN 4243
// Harvard Architecture Data Memory (Big Endian)
//------------------------------------------------

module dmem (
    clk,
    r_w,
    mem_addr,
    mem_data,
    mem_out
);

    input clk;
    input r_w;
    input [31:0] mem_addr;
    input [31:0] mem_data;
    output reg [31:0] mem_out;
    wire [ 1:0] sel_mem;
    reg  [ 3:0] ce_mem;
    reg  [ 3:0] we_mem;

    wire [31:0] inter_dmem0;
    wire [31:0] inter_dmem1;
    wire [31:0] inter_dmem2;
    wire [31:0] inter_dmem3;

    assign sel_mem = (mem_addr[31] == 1) ? 2'b11 :
                     (mem_addr[23] == 1) ? 2'b10 :
                     (mem_addr[15] == 1) ? 2'b01 :
                     2'b00;

    always @* begin
        case (sel_mem)
            2'b00: mem_out = inter_dmem0;
            2'b01: mem_out = inter_dmem1;
            2'b10: mem_out = inter_dmem2;
            2'b11: mem_out = inter_dmem3;
        endcase  // case (sel_mem)
    end

    always @* begin
        case (sel_mem)
            2'b00: ce_mem = 4'b0001;
            2'b01: ce_mem = 4'b0010;
            2'b10: ce_mem = 4'b0100;
            2'b11: ce_mem = 4'b1000;
        endcase  // case (sel_mem)
    end

    always @* begin
        case (sel_mem)
            2'b00: we_mem = 4'b0001;
            2'b01: we_mem = 4'b0010;
            2'b10: we_mem = 4'b0100;
            2'b11: we_mem = 4'b1000;
        endcase  // case (sel_mem)
    end

    la_spram #(
        .DW(32),
        .AW(8)
    ) dmem0 (
        .clk(clk),
        .ce(ce_mem[0]),
        .we(we_mem[0] && r_w),
        .wmask(32'hffffffff),
        .addr(mem_addr[7:0]),
        .din(mem_data),
        .dout(inter_dmem0),
        .selctrl(1'b0),
        .ctrl('b0),
        .status()
    );
    la_spram #(
        .DW(32),
        .AW(8)
    ) dmem1 (
        .clk(clk),
        .ce(ce_mem[1]),
        .we(we_mem[1] && r_w),
        .wmask(32'hffffffff),
        .addr(mem_addr[15:8]),
        .din(mem_data),
        .dout(inter_dmem1),
        .selctrl(1'b0),
        .ctrl('b0),
        .status()
    );
    la_spram #(
        .DW(32),
        .AW(8)
    ) dmem2 (
        .clk(clk),
        .ce(ce_mem[2]),
        .we(we_mem[2] && r_w),
        .wmask(32'hffffffff),
        .addr(mem_addr[23:16]),
        .din(mem_data),
        .dout(inter_dmem2),
        .selctrl(1'b0),
        .ctrl('b0),
        .status()
    );
    la_spram #(
        .DW(32),
        .AW(8)
    ) dmem3 (
        .clk(clk),
        .ce(ce_mem[3]),
        .we(we_mem[3] && r_w),
        .wmask(32'hffffffff),
        .addr(mem_addr[31:24]),
        .din(mem_data),
        .dout(inter_dmem3),
        .selctrl(1'b0),
        .ctrl('b0),
        .status()
    );

endmodule  // mem
