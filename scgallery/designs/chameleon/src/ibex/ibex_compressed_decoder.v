module ibex_compressed_decoder (
	clk_i,
	rst_ni,
	valid_i,
	instr_i,
	instr_o,
	is_compressed_o,
	illegal_instr_o
);
	input wire clk_i;
	input wire rst_ni;
	input wire valid_i;
	input wire [31:0] instr_i;
	output reg [31:0] instr_o;
	output wire is_compressed_o;
	output reg illegal_instr_o;
	localparam integer RegFileFF = 0;
	localparam integer RegFileFPGA = 1;
	localparam integer RegFileLatch = 2;
	localparam integer RV32MNone = 0;
	localparam integer RV32MSlow = 1;
	localparam integer RV32MFast = 2;
	localparam integer RV32MSingleCycle = 3;
	localparam integer RV32BNone = 0;
	localparam integer RV32BBalanced = 1;
	localparam integer RV32BFull = 2;
	localparam [6:0] OPCODE_LOAD = 7'h03;
	localparam [6:0] OPCODE_MISC_MEM = 7'h0f;
	localparam [6:0] OPCODE_OP_IMM = 7'h13;
	localparam [6:0] OPCODE_AUIPC = 7'h17;
	localparam [6:0] OPCODE_STORE = 7'h23;
	localparam [6:0] OPCODE_OP = 7'h33;
	localparam [6:0] OPCODE_LUI = 7'h37;
	localparam [6:0] OPCODE_BRANCH = 7'h63;
	localparam [6:0] OPCODE_JALR = 7'h67;
	localparam [6:0] OPCODE_JAL = 7'h6f;
	localparam [6:0] OPCODE_SYSTEM = 7'h73;
	localparam [5:0] ALU_ADD = 0;
	localparam [5:0] ALU_SUB = 1;
	localparam [5:0] ALU_XOR = 2;
	localparam [5:0] ALU_OR = 3;
	localparam [5:0] ALU_AND = 4;
	localparam [5:0] ALU_XNOR = 5;
	localparam [5:0] ALU_ORN = 6;
	localparam [5:0] ALU_ANDN = 7;
	localparam [5:0] ALU_SRA = 8;
	localparam [5:0] ALU_SRL = 9;
	localparam [5:0] ALU_SLL = 10;
	localparam [5:0] ALU_SRO = 11;
	localparam [5:0] ALU_SLO = 12;
	localparam [5:0] ALU_ROR = 13;
	localparam [5:0] ALU_ROL = 14;
	localparam [5:0] ALU_GREV = 15;
	localparam [5:0] ALU_GORC = 16;
	localparam [5:0] ALU_SHFL = 17;
	localparam [5:0] ALU_UNSHFL = 18;
	localparam [5:0] ALU_LT = 19;
	localparam [5:0] ALU_LTU = 20;
	localparam [5:0] ALU_GE = 21;
	localparam [5:0] ALU_GEU = 22;
	localparam [5:0] ALU_EQ = 23;
	localparam [5:0] ALU_NE = 24;
	localparam [5:0] ALU_MIN = 25;
	localparam [5:0] ALU_MINU = 26;
	localparam [5:0] ALU_MAX = 27;
	localparam [5:0] ALU_MAXU = 28;
	localparam [5:0] ALU_PACK = 29;
	localparam [5:0] ALU_PACKU = 30;
	localparam [5:0] ALU_PACKH = 31;
	localparam [5:0] ALU_SEXTB = 32;
	localparam [5:0] ALU_SEXTH = 33;
	localparam [5:0] ALU_CLZ = 34;
	localparam [5:0] ALU_CTZ = 35;
	localparam [5:0] ALU_PCNT = 36;
	localparam [5:0] ALU_SLT = 37;
	localparam [5:0] ALU_SLTU = 38;
	localparam [5:0] ALU_CMOV = 39;
	localparam [5:0] ALU_CMIX = 40;
	localparam [5:0] ALU_FSL = 41;
	localparam [5:0] ALU_FSR = 42;
	localparam [5:0] ALU_SBSET = 43;
	localparam [5:0] ALU_SBCLR = 44;
	localparam [5:0] ALU_SBINV = 45;
	localparam [5:0] ALU_SBEXT = 46;
	localparam [5:0] ALU_BEXT = 47;
	localparam [5:0] ALU_BDEP = 48;
	localparam [5:0] ALU_BFP = 49;
	localparam [5:0] ALU_CLMUL = 50;
	localparam [5:0] ALU_CLMULR = 51;
	localparam [5:0] ALU_CLMULH = 52;
	localparam [5:0] ALU_CRC32_B = 53;
	localparam [5:0] ALU_CRC32C_B = 54;
	localparam [5:0] ALU_CRC32_H = 55;
	localparam [5:0] ALU_CRC32C_H = 56;
	localparam [5:0] ALU_CRC32_W = 57;
	localparam [5:0] ALU_CRC32C_W = 58;
	localparam [1:0] MD_OP_MULL = 0;
	localparam [1:0] MD_OP_MULH = 1;
	localparam [1:0] MD_OP_DIV = 2;
	localparam [1:0] MD_OP_REM = 3;
	localparam [1:0] CSR_OP_READ = 0;
	localparam [1:0] CSR_OP_WRITE = 1;
	localparam [1:0] CSR_OP_SET = 2;
	localparam [1:0] CSR_OP_CLEAR = 3;
	localparam [1:0] PRIV_LVL_M = 2'b11;
	localparam [1:0] PRIV_LVL_H = 2'b10;
	localparam [1:0] PRIV_LVL_S = 2'b01;
	localparam [1:0] PRIV_LVL_U = 2'b00;
	localparam [3:0] XDEBUGVER_NO = 4'd0;
	localparam [3:0] XDEBUGVER_STD = 4'd4;
	localparam [3:0] XDEBUGVER_NONSTD = 4'd15;
	localparam [1:0] WB_INSTR_LOAD = 0;
	localparam [1:0] WB_INSTR_STORE = 1;
	localparam [1:0] WB_INSTR_OTHER = 2;
	localparam [1:0] OP_A_REG_A = 0;
	localparam [1:0] OP_A_FWD = 1;
	localparam [1:0] OP_A_CURRPC = 2;
	localparam [1:0] OP_A_IMM = 3;
	localparam [0:0] IMM_A_Z = 0;
	localparam [0:0] IMM_A_ZERO = 1;
	localparam [0:0] OP_B_REG_B = 0;
	localparam [0:0] OP_B_IMM = 1;
	localparam [2:0] IMM_B_I = 0;
	localparam [2:0] IMM_B_S = 1;
	localparam [2:0] IMM_B_B = 2;
	localparam [2:0] IMM_B_U = 3;
	localparam [2:0] IMM_B_J = 4;
	localparam [2:0] IMM_B_INCR_PC = 5;
	localparam [2:0] IMM_B_INCR_ADDR = 6;
	localparam [0:0] RF_WD_EX = 0;
	localparam [0:0] RF_WD_CSR = 1;
	localparam [2:0] PC_BOOT = 0;
	localparam [2:0] PC_JUMP = 1;
	localparam [2:0] PC_EXC = 2;
	localparam [2:0] PC_ERET = 3;
	localparam [2:0] PC_DRET = 4;
	localparam [2:0] PC_BP = 5;
	localparam [1:0] EXC_PC_EXC = 0;
	localparam [1:0] EXC_PC_IRQ = 1;
	localparam [1:0] EXC_PC_DBD = 2;
	localparam [1:0] EXC_PC_DBG_EXC = 3;
	localparam [5:0] EXC_CAUSE_IRQ_SOFTWARE_M = {1'b1, 5'd3};
	localparam [5:0] EXC_CAUSE_IRQ_TIMER_M = {1'b1, 5'd7};
	localparam [5:0] EXC_CAUSE_IRQ_EXTERNAL_M = {1'b1, 5'd11};
	localparam [5:0] EXC_CAUSE_IRQ_NM = {1'b1, 5'd31};
	localparam [5:0] EXC_CAUSE_INSN_ADDR_MISA = {1'b0, 5'd0};
	localparam [5:0] EXC_CAUSE_INSTR_ACCESS_FAULT = {1'b0, 5'd1};
	localparam [5:0] EXC_CAUSE_ILLEGAL_INSN = {1'b0, 5'd2};
	localparam [5:0] EXC_CAUSE_BREAKPOINT = {1'b0, 5'd3};
	localparam [5:0] EXC_CAUSE_LOAD_ACCESS_FAULT = {1'b0, 5'd5};
	localparam [5:0] EXC_CAUSE_STORE_ACCESS_FAULT = {1'b0, 5'd7};
	localparam [5:0] EXC_CAUSE_ECALL_UMODE = {1'b0, 5'd8};
	localparam [5:0] EXC_CAUSE_ECALL_MMODE = {1'b0, 5'd11};
	localparam [2:0] DBG_CAUSE_NONE = 3'h0;
	localparam [2:0] DBG_CAUSE_EBREAK = 3'h1;
	localparam [2:0] DBG_CAUSE_TRIGGER = 3'h2;
	localparam [2:0] DBG_CAUSE_HALTREQ = 3'h3;
	localparam [2:0] DBG_CAUSE_STEP = 3'h4;
	localparam [31:0] PMP_MAX_REGIONS = 16;
	localparam [31:0] PMP_CFG_W = 8;
	localparam [31:0] PMP_I = 0;
	localparam [31:0] PMP_D = 1;
	localparam [1:0] PMP_ACC_EXEC = 2'b00;
	localparam [1:0] PMP_ACC_WRITE = 2'b01;
	localparam [1:0] PMP_ACC_READ = 2'b10;
	localparam [1:0] PMP_MODE_OFF = 2'b00;
	localparam [1:0] PMP_MODE_TOR = 2'b01;
	localparam [1:0] PMP_MODE_NA4 = 2'b10;
	localparam [1:0] PMP_MODE_NAPOT = 2'b11;
	localparam [11:0] CSR_MHARTID = 12'hf14;
	localparam [11:0] CSR_MSTATUS = 12'h300;
	localparam [11:0] CSR_MISA = 12'h301;
	localparam [11:0] CSR_MIE = 12'h304;
	localparam [11:0] CSR_MTVEC = 12'h305;
	localparam [11:0] CSR_MSCRATCH = 12'h340;
	localparam [11:0] CSR_MEPC = 12'h341;
	localparam [11:0] CSR_MCAUSE = 12'h342;
	localparam [11:0] CSR_MTVAL = 12'h343;
	localparam [11:0] CSR_MIP = 12'h344;
	localparam [11:0] CSR_PMPCFG0 = 12'h3a0;
	localparam [11:0] CSR_PMPCFG1 = 12'h3a1;
	localparam [11:0] CSR_PMPCFG2 = 12'h3a2;
	localparam [11:0] CSR_PMPCFG3 = 12'h3a3;
	localparam [11:0] CSR_PMPADDR0 = 12'h3b0;
	localparam [11:0] CSR_PMPADDR1 = 12'h3b1;
	localparam [11:0] CSR_PMPADDR2 = 12'h3b2;
	localparam [11:0] CSR_PMPADDR3 = 12'h3b3;
	localparam [11:0] CSR_PMPADDR4 = 12'h3b4;
	localparam [11:0] CSR_PMPADDR5 = 12'h3b5;
	localparam [11:0] CSR_PMPADDR6 = 12'h3b6;
	localparam [11:0] CSR_PMPADDR7 = 12'h3b7;
	localparam [11:0] CSR_PMPADDR8 = 12'h3b8;
	localparam [11:0] CSR_PMPADDR9 = 12'h3b9;
	localparam [11:0] CSR_PMPADDR10 = 12'h3ba;
	localparam [11:0] CSR_PMPADDR11 = 12'h3bb;
	localparam [11:0] CSR_PMPADDR12 = 12'h3bc;
	localparam [11:0] CSR_PMPADDR13 = 12'h3bd;
	localparam [11:0] CSR_PMPADDR14 = 12'h3be;
	localparam [11:0] CSR_PMPADDR15 = 12'h3bf;
	localparam [11:0] CSR_TSELECT = 12'h7a0;
	localparam [11:0] CSR_TDATA1 = 12'h7a1;
	localparam [11:0] CSR_TDATA2 = 12'h7a2;
	localparam [11:0] CSR_TDATA3 = 12'h7a3;
	localparam [11:0] CSR_MCONTEXT = 12'h7a8;
	localparam [11:0] CSR_SCONTEXT = 12'h7aa;
	localparam [11:0] CSR_DCSR = 12'h7b0;
	localparam [11:0] CSR_DPC = 12'h7b1;
	localparam [11:0] CSR_DSCRATCH0 = 12'h7b2;
	localparam [11:0] CSR_DSCRATCH1 = 12'h7b3;
	localparam [11:0] CSR_MCOUNTINHIBIT = 12'h320;
	localparam [11:0] CSR_MHPMEVENT3 = 12'h323;
	localparam [11:0] CSR_MHPMEVENT4 = 12'h324;
	localparam [11:0] CSR_MHPMEVENT5 = 12'h325;
	localparam [11:0] CSR_MHPMEVENT6 = 12'h326;
	localparam [11:0] CSR_MHPMEVENT7 = 12'h327;
	localparam [11:0] CSR_MHPMEVENT8 = 12'h328;
	localparam [11:0] CSR_MHPMEVENT9 = 12'h329;
	localparam [11:0] CSR_MHPMEVENT10 = 12'h32a;
	localparam [11:0] CSR_MHPMEVENT11 = 12'h32b;
	localparam [11:0] CSR_MHPMEVENT12 = 12'h32c;
	localparam [11:0] CSR_MHPMEVENT13 = 12'h32d;
	localparam [11:0] CSR_MHPMEVENT14 = 12'h32e;
	localparam [11:0] CSR_MHPMEVENT15 = 12'h32f;
	localparam [11:0] CSR_MHPMEVENT16 = 12'h330;
	localparam [11:0] CSR_MHPMEVENT17 = 12'h331;
	localparam [11:0] CSR_MHPMEVENT18 = 12'h332;
	localparam [11:0] CSR_MHPMEVENT19 = 12'h333;
	localparam [11:0] CSR_MHPMEVENT20 = 12'h334;
	localparam [11:0] CSR_MHPMEVENT21 = 12'h335;
	localparam [11:0] CSR_MHPMEVENT22 = 12'h336;
	localparam [11:0] CSR_MHPMEVENT23 = 12'h337;
	localparam [11:0] CSR_MHPMEVENT24 = 12'h338;
	localparam [11:0] CSR_MHPMEVENT25 = 12'h339;
	localparam [11:0] CSR_MHPMEVENT26 = 12'h33a;
	localparam [11:0] CSR_MHPMEVENT27 = 12'h33b;
	localparam [11:0] CSR_MHPMEVENT28 = 12'h33c;
	localparam [11:0] CSR_MHPMEVENT29 = 12'h33d;
	localparam [11:0] CSR_MHPMEVENT30 = 12'h33e;
	localparam [11:0] CSR_MHPMEVENT31 = 12'h33f;
	localparam [11:0] CSR_MCYCLE = 12'hb00;
	localparam [11:0] CSR_MINSTRET = 12'hb02;
	localparam [11:0] CSR_MHPMCOUNTER3 = 12'hb03;
	localparam [11:0] CSR_MHPMCOUNTER4 = 12'hb04;
	localparam [11:0] CSR_MHPMCOUNTER5 = 12'hb05;
	localparam [11:0] CSR_MHPMCOUNTER6 = 12'hb06;
	localparam [11:0] CSR_MHPMCOUNTER7 = 12'hb07;
	localparam [11:0] CSR_MHPMCOUNTER8 = 12'hb08;
	localparam [11:0] CSR_MHPMCOUNTER9 = 12'hb09;
	localparam [11:0] CSR_MHPMCOUNTER10 = 12'hb0a;
	localparam [11:0] CSR_MHPMCOUNTER11 = 12'hb0b;
	localparam [11:0] CSR_MHPMCOUNTER12 = 12'hb0c;
	localparam [11:0] CSR_MHPMCOUNTER13 = 12'hb0d;
	localparam [11:0] CSR_MHPMCOUNTER14 = 12'hb0e;
	localparam [11:0] CSR_MHPMCOUNTER15 = 12'hb0f;
	localparam [11:0] CSR_MHPMCOUNTER16 = 12'hb10;
	localparam [11:0] CSR_MHPMCOUNTER17 = 12'hb11;
	localparam [11:0] CSR_MHPMCOUNTER18 = 12'hb12;
	localparam [11:0] CSR_MHPMCOUNTER19 = 12'hb13;
	localparam [11:0] CSR_MHPMCOUNTER20 = 12'hb14;
	localparam [11:0] CSR_MHPMCOUNTER21 = 12'hb15;
	localparam [11:0] CSR_MHPMCOUNTER22 = 12'hb16;
	localparam [11:0] CSR_MHPMCOUNTER23 = 12'hb17;
	localparam [11:0] CSR_MHPMCOUNTER24 = 12'hb18;
	localparam [11:0] CSR_MHPMCOUNTER25 = 12'hb19;
	localparam [11:0] CSR_MHPMCOUNTER26 = 12'hb1a;
	localparam [11:0] CSR_MHPMCOUNTER27 = 12'hb1b;
	localparam [11:0] CSR_MHPMCOUNTER28 = 12'hb1c;
	localparam [11:0] CSR_MHPMCOUNTER29 = 12'hb1d;
	localparam [11:0] CSR_MHPMCOUNTER30 = 12'hb1e;
	localparam [11:0] CSR_MHPMCOUNTER31 = 12'hb1f;
	localparam [11:0] CSR_MCYCLEH = 12'hb80;
	localparam [11:0] CSR_MINSTRETH = 12'hb82;
	localparam [11:0] CSR_MHPMCOUNTER3H = 12'hb83;
	localparam [11:0] CSR_MHPMCOUNTER4H = 12'hb84;
	localparam [11:0] CSR_MHPMCOUNTER5H = 12'hb85;
	localparam [11:0] CSR_MHPMCOUNTER6H = 12'hb86;
	localparam [11:0] CSR_MHPMCOUNTER7H = 12'hb87;
	localparam [11:0] CSR_MHPMCOUNTER8H = 12'hb88;
	localparam [11:0] CSR_MHPMCOUNTER9H = 12'hb89;
	localparam [11:0] CSR_MHPMCOUNTER10H = 12'hb8a;
	localparam [11:0] CSR_MHPMCOUNTER11H = 12'hb8b;
	localparam [11:0] CSR_MHPMCOUNTER12H = 12'hb8c;
	localparam [11:0] CSR_MHPMCOUNTER13H = 12'hb8d;
	localparam [11:0] CSR_MHPMCOUNTER14H = 12'hb8e;
	localparam [11:0] CSR_MHPMCOUNTER15H = 12'hb8f;
	localparam [11:0] CSR_MHPMCOUNTER16H = 12'hb90;
	localparam [11:0] CSR_MHPMCOUNTER17H = 12'hb91;
	localparam [11:0] CSR_MHPMCOUNTER18H = 12'hb92;
	localparam [11:0] CSR_MHPMCOUNTER19H = 12'hb93;
	localparam [11:0] CSR_MHPMCOUNTER20H = 12'hb94;
	localparam [11:0] CSR_MHPMCOUNTER21H = 12'hb95;
	localparam [11:0] CSR_MHPMCOUNTER22H = 12'hb96;
	localparam [11:0] CSR_MHPMCOUNTER23H = 12'hb97;
	localparam [11:0] CSR_MHPMCOUNTER24H = 12'hb98;
	localparam [11:0] CSR_MHPMCOUNTER25H = 12'hb99;
	localparam [11:0] CSR_MHPMCOUNTER26H = 12'hb9a;
	localparam [11:0] CSR_MHPMCOUNTER27H = 12'hb9b;
	localparam [11:0] CSR_MHPMCOUNTER28H = 12'hb9c;
	localparam [11:0] CSR_MHPMCOUNTER29H = 12'hb9d;
	localparam [11:0] CSR_MHPMCOUNTER30H = 12'hb9e;
	localparam [11:0] CSR_MHPMCOUNTER31H = 12'hb9f;
	localparam [11:0] CSR_CPUCTRL = 12'h7c0;
	localparam [11:0] CSR_SECURESEED = 12'h7c1;
	localparam [11:0] CSR_OFF_PMP_CFG = 12'h3a0;
	localparam [11:0] CSR_OFF_PMP_ADDR = 12'h3b0;
	localparam [31:0] CSR_MSTATUS_MIE_BIT = 3;
	localparam [31:0] CSR_MSTATUS_MPIE_BIT = 7;
	localparam [31:0] CSR_MSTATUS_MPP_BIT_LOW = 11;
	localparam [31:0] CSR_MSTATUS_MPP_BIT_HIGH = 12;
	localparam [31:0] CSR_MSTATUS_MPRV_BIT = 17;
	localparam [31:0] CSR_MSTATUS_TW_BIT = 21;
	localparam [1:0] CSR_MISA_MXL = 2'd1;
	localparam [31:0] CSR_MSIX_BIT = 3;
	localparam [31:0] CSR_MTIX_BIT = 7;
	localparam [31:0] CSR_MEIX_BIT = 11;
	localparam [31:0] CSR_MFIX_BIT_LOW = 16;
	localparam [31:0] CSR_MFIX_BIT_HIGH = 30;
	wire unused_valid;
	assign unused_valid = valid_i;
	always @(*) begin
		instr_o = instr_i;
		illegal_instr_o = 1'b0;
		case (instr_i[1:0])
			2'b00:
				case (instr_i[15:13])
					3'b000: begin
						instr_o = {2'b00, instr_i[10:7], instr_i[12:11], instr_i[5], instr_i[6], 2'b00, 5'h02, 3'b000, 2'b01, instr_i[4:2], OPCODE_OP_IMM};
						if (instr_i[12:5] == 8'b00000000)
							illegal_instr_o = 1'b1;
					end
					3'b010: instr_o = {5'b00000, instr_i[5], instr_i[12:10], instr_i[6], 2'b00, 2'b01, instr_i[9:7], 3'b010, 2'b01, instr_i[4:2], OPCODE_LOAD};
					3'b110: instr_o = {5'b00000, instr_i[5], instr_i[12], 2'b01, instr_i[4:2], 2'b01, instr_i[9:7], 3'b010, instr_i[11:10], instr_i[6], 2'b00, OPCODE_STORE};
					3'b001, 3'b011, 3'b100, 3'b101, 3'b111: illegal_instr_o = 1'b1;
					default: illegal_instr_o = 1'b1;
				endcase
			2'b01:
				case (instr_i[15:13])
					3'b000: instr_o = {{6 {instr_i[12]}}, instr_i[12], instr_i[6:2], instr_i[11:7], 3'b000, instr_i[11:7], OPCODE_OP_IMM};
					3'b001, 3'b101: instr_o = {instr_i[12], instr_i[8], instr_i[10:9], instr_i[6], instr_i[7], instr_i[2], instr_i[11], instr_i[5:3], {9 {instr_i[12]}}, 4'b0000, ~instr_i[15], OPCODE_JAL};
					3'b010: instr_o = {{6 {instr_i[12]}}, instr_i[12], instr_i[6:2], 5'b00000, 3'b000, instr_i[11:7], OPCODE_OP_IMM};
					3'b011: begin
						instr_o = {{15 {instr_i[12]}}, instr_i[6:2], instr_i[11:7], OPCODE_LUI};
						if (instr_i[11:7] == 5'h02)
							instr_o = {{3 {instr_i[12]}}, instr_i[4:3], instr_i[5], instr_i[2], instr_i[6], 4'b0000, 5'h02, 3'b000, 5'h02, OPCODE_OP_IMM};
						if ({instr_i[12], instr_i[6:2]} == 6'b000000)
							illegal_instr_o = 1'b1;
					end
					3'b100:
						case (instr_i[11:10])
							2'b00, 2'b01: begin
								instr_o = {1'b0, instr_i[10], 5'b00000, instr_i[6:2], 2'b01, instr_i[9:7], 3'b101, 2'b01, instr_i[9:7], OPCODE_OP_IMM};
								if (instr_i[12] == 1'b1)
									illegal_instr_o = 1'b1;
							end
							2'b10: instr_o = {{6 {instr_i[12]}}, instr_i[12], instr_i[6:2], 2'b01, instr_i[9:7], 3'b111, 2'b01, instr_i[9:7], OPCODE_OP_IMM};
							2'b11:
								case ({instr_i[12], instr_i[6:5]})
									3'b000: instr_o = {2'b01, 5'b00000, 2'b01, instr_i[4:2], 2'b01, instr_i[9:7], 3'b000, 2'b01, instr_i[9:7], OPCODE_OP};
									3'b001: instr_o = {7'b0000000, 2'b01, instr_i[4:2], 2'b01, instr_i[9:7], 3'b100, 2'b01, instr_i[9:7], OPCODE_OP};
									3'b010: instr_o = {7'b0000000, 2'b01, instr_i[4:2], 2'b01, instr_i[9:7], 3'b110, 2'b01, instr_i[9:7], OPCODE_OP};
									3'b011: instr_o = {7'b0000000, 2'b01, instr_i[4:2], 2'b01, instr_i[9:7], 3'b111, 2'b01, instr_i[9:7], OPCODE_OP};
									3'b100, 3'b101, 3'b110, 3'b111: illegal_instr_o = 1'b1;
									default: illegal_instr_o = 1'b1;
								endcase
							default: illegal_instr_o = 1'b1;
						endcase
					3'b110, 3'b111: instr_o = {{4 {instr_i[12]}}, instr_i[6:5], instr_i[2], 5'b00000, 2'b01, instr_i[9:7], 2'b00, instr_i[13], instr_i[11:10], instr_i[4:3], instr_i[12], OPCODE_BRANCH};
					default: illegal_instr_o = 1'b1;
				endcase
			2'b10:
				case (instr_i[15:13])
					3'b000: begin
						instr_o = {7'b0000000, instr_i[6:2], instr_i[11:7], 3'b001, instr_i[11:7], OPCODE_OP_IMM};
						if (instr_i[12] == 1'b1)
							illegal_instr_o = 1'b1;
					end
					3'b010: begin
						instr_o = {4'b0000, instr_i[3:2], instr_i[12], instr_i[6:4], 2'b00, 5'h02, 3'b010, instr_i[11:7], OPCODE_LOAD};
						if (instr_i[11:7] == 5'b00000)
							illegal_instr_o = 1'b1;
					end
					3'b100:
						if (instr_i[12] == 1'b0) begin
							if (instr_i[6:2] != 5'b00000)
								instr_o = {7'b0000000, instr_i[6:2], 5'b00000, 3'b000, instr_i[11:7], OPCODE_OP};
							else begin
								instr_o = {12'b000000000000, instr_i[11:7], 3'b000, 5'b00000, OPCODE_JALR};
								if (instr_i[11:7] == 5'b00000)
									illegal_instr_o = 1'b1;
							end
						end
						else if (instr_i[6:2] != 5'b00000)
							instr_o = {7'b0000000, instr_i[6:2], instr_i[11:7], 3'b000, instr_i[11:7], OPCODE_OP};
						else if (instr_i[11:7] == 5'b00000)
							instr_o = 32'h00100073;
						else
							instr_o = {12'b000000000000, instr_i[11:7], 3'b000, 5'b00001, OPCODE_JALR};
					3'b110: instr_o = {4'b0000, instr_i[8:7], instr_i[12], instr_i[6:2], 5'h02, 3'b010, instr_i[11:9], 2'b00, OPCODE_STORE};
					3'b001, 3'b011, 3'b101, 3'b111: illegal_instr_o = 1'b1;
					default: illegal_instr_o = 1'b1;
				endcase
			2'b11:
				;
			default: illegal_instr_o = 1'b1;
		endcase
	end
	assign is_compressed_o = instr_i[1:0] != 2'b11;
endmodule
