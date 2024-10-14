import os
from siliconcompiler import Library

from scgallery.designs.serv import src as serv_src
from scgallery.designs.serv.src import serv


def setup():
    lib = Library("serv_reg_file", package="serv", auto_enable=True)
    serv_src.register(lib)

    lib.use(serv)

    for src in ('serv_rf_ram_if.v',
                'serv_rf_ram.v',
                'serv_rf_top.v'):
        lib.input(os.path.join('rtl', src), package='serv')

    return lib
