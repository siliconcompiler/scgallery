set clk_period 34.0
set clk_io_pct 0.2

set clk_port [get_ports clock]

create_clock -name core_clk -period $clk_period $clk_port

set non_clock_inputs [lsearch -inline -all -not -exact [all_inputs] $clk_port]
set_input_delay [expr {$clk_period * $clk_io_pct}] -clock core_clk $non_clock_inputs
set_output_delay [expr {$clk_period * $clk_io_pct}] -clock core_clk [all_outputs]

set_driving_cell -lib_cell sky130_fd_sc_hd__buf_2 [all_inputs]
