set clk_period 86
set clk_io_pct 0.2

set clk_port [get_ports clk_i]

create_clock -name CLK -period $clk_period $clk_port

set non_clock_inputs [lsearch -inline -all -not -exact [all_inputs] $clk_port]
set_input_delay [expr {$clk_period * $clk_io_pct}] -clock CLK $non_clock_inputs
set_output_delay [expr {$clk_period * $clk_io_pct}] -clock CLK [all_outputs]

set_driving_cell -lib_cell sky130_fd_sc_hd__buf_2 [all_inputs]
