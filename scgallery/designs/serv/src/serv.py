import os
from siliconcompiler import Library

from scgallery.designs.serv import src as serv_src


def setup():
    lib = Library("serv_core", package="serv", auto_enable=True)
    serv_src.register(lib)

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
                'serv_synth_wrapper.v',
                'serv_top.v'):
        lib.input(os.path.join('rtl', src), package='serv')

    return lib
