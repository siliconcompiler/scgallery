from siliconcompiler import Library


def setup(chip):
    stackup = '5M1LI'

    lib = Library(chip, 'microwatt_ip')

    path_base = 'scgallery/designs/microwatt/libraries/skywater130/'
    for ip in ('Microwatt_FP_DFFRFile',
               'multiply_add_64x64',
               'RAM32_1RW1R',
               'RAM512'):
        lib.add('output', stackup, 'lef', f'{path_base}/lef/{ip}.lef')
        lib.add('output', stackup, 'gds', f'{path_base}/gds/{ip}.gds.gz')

        liberty = f'{path_base}/lib/{ip}.lib'
        lib.add('output', 'slow', 'nldm', liberty)
        lib.add('output', 'typical', 'nldm', liberty)
        lib.add('output', 'fast', 'nldm', liberty)

    # lib.set('option', 'file', 'openroad_pdngen', f'{path_base}/pdngen.tcl')

    return lib
