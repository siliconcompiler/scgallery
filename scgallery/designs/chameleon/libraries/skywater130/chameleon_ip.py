from siliconcompiler import Library
import os


def setup(chip):
    stackup = '5M1LI'

    libs = []

    chip.register_package_source(name='chameleon_ip', path=os.path.dirname(__file__))

    for ip in ('apb_sys_0',
               'DFFRAM_4K',
               'DMC_32x16HC',
               'ibex_wrapper'):
        lib = Library(chip, ip, package='chameleon_ip')
        lib.add('output', stackup, 'lef', f'lef/{ip}.lef')
        lib.add('output', stackup, 'gds', f'gds/{ip}.gds.gz')
        lib.add('output', 'blackbox', 'verilog', f'verilog/{ip}.v')

        libs.append(lib)

    return libs
