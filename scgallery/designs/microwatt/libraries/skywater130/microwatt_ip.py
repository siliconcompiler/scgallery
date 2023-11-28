from siliconcompiler import Library
import os


def setup(chip):
    stackup = '5M1LI'

    libs = []

    chip.register_package_source(name='microwatt_ip', path=os.path.dirname(__file__))

    for ip in ('Microwatt_FP_DFFRFile',
               'multiply_add_64x64',
               'RAM32_1RW1R',
               'RAM512'):
        lib = Library(chip, ip, package='microwatt_ip')
        lib.add('output', stackup, 'lef', f'lef/{ip}.lef')
        lib.add('output', stackup, 'gds', f'gds/{ip}.gds.gz')

        liberty = f'lib/{ip}.lib'
        lib.add('output', 'slow', 'nldm', liberty)
        lib.add('output', 'typical', 'nldm', liberty)
        lib.add('output', 'fast', 'nldm', liberty)

        libs.append(lib)

    return libs
