set clk_io_pct 0.2

set clk_period 30.0
set clk_port [get_ports wb_clk_i]
create_clock -name wb_clk_i -period $clk_period $clk_port
set non_clock_inputs [lsearch -inline -all -not -exact [all_inputs] $clk_port]
set_input_delay [expr {$clk_period * $clk_io_pct}] -clock wb_clk_i $non_clock_inputs
set_output_delay [expr {$clk_period * $clk_io_pct}] -clock wb_clk_i [all_outputs]

set tx_clk_period 20.0
set tx_clk_port [get_ports mtx_clk_pad_i]
create_clock -name mtx_clk_pad_i -period $tx_clk_period $tx_clk_port
set mtx_non_clock_inputs [lsearch -inline -all -not -exact [all_inputs] $tx_clk_port]
set_input_delay [expr {$tx_clk_period * $clk_io_pct}] -clock mtx_clk_pad_i $mtx_non_clock_inputs
set_output_delay [expr {$tx_clk_period * $clk_io_pct}] -clock mtx_clk_pad_i [all_outputs]

set rx_clk_period 20.0
set rx_clk_port [get_ports mrx_clk_pad_i]
create_clock -name mrx_clk_pad_i -period $rx_clk_period $rx_clk_port
set mrx_non_clock_inputs [lsearch -inline -all -not -exact [all_inputs] $rx_clk_port]
set_input_delay [expr {$rx_clk_period * $clk_io_pct}] -clock mrx_clk_pad_i $mrx_non_clock_inputs
set_output_delay [expr {$rx_clk_period * $clk_io_pct}] -clock mrx_clk_pad_i [all_outputs]

set_clock_groups -name core_clock -logically_exclusive \
    -group [get_clocks wb_clk_i] \
    -group [get_clocks mtx_clk_pad_i] \
    -group [get_clocks mrx_clk_pad_i]

set_driving_cell -lib_cell sky130_fd_sc_hd__buf_2 [all_inputs]
