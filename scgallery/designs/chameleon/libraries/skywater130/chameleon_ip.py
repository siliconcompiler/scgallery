from siliconcompiler import Library
import os


def setup(chip):
    stackup = '5M1LI'

    libs = []

    path_base = os.path.dirname(__file__)
    for ip in ('apb_sys_0',
               'DFFRAM_4K',
               'DMC_32x16HC',
               'ibex_wrapper'):
        lib = Library(chip, ip)
        lib.add('output', stackup, 'lef', f'{path_base}/lef/{ip}.lef')
        lib.add('output', stackup, 'gds', f'{path_base}/gds/{ip}.gds.gz')
        lib.add('output', 'blackbox', 'verilog', f'{path_base}/verilog/{ip}.v')

        libs.append(lib)

    return libs
