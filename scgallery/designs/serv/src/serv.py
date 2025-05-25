import os
from siliconcompiler import Library


def setup():
    lib = Library("serv_core", package="serv", auto_enable=True)

    lib.register_source(
        name='serv',
        path='git+https://github.com/olofk/serv.git',
        ref='a72c1e8737d424c31bf6ff909795acc37aa4cc90')

    for src in ('serv_aligner.v',
                'serv_alu.v',
                'serv_bufreg2.v',
                'serv_bufreg.v',
                'serv_compdec.v',
                'serv_csr.v',
                'serv_ctrl.v',
                'serv_debug.v',
                'serv_decode.v',
                'serv_immdec.v',
                'serv_mem_if.v',
                'serv_rf_if.v',
                'serv_state.v',
                'serv_top.v',
                'serv_rf_ram_if.v'):
        lib.input(os.path.join('rtl', src), package='serv')

    return lib
