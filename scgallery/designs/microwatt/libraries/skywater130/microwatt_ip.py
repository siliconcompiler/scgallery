from siliconcompiler import Library
import os


def setup(chip):
    stackup = '5M1LI'

    libs = []

    path_base = os.path.dirname(__file__)
    for ip in ('Microwatt_FP_DFFRFile',
               'multiply_add_64x64',
               'RAM32_1RW1R',
               'RAM512'):
        lib = Library(chip, ip)
        lib.add('output', stackup, 'lef', f'{path_base}/lef/{ip}.lef')
        lib.add('output', stackup, 'gds', f'{path_base}/gds/{ip}.gds.gz')

        liberty = f'{path_base}/lib/{ip}.lib'
        lib.add('output', 'slow', 'nldm', liberty)
        lib.add('output', 'typical', 'nldm', liberty)
        lib.add('output', 'fast', 'nldm', liberty)

        libs.append(lib)

    return libs
