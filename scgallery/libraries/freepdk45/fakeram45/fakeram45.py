from siliconcompiler import Library


def setup(chip):
    libs = []
    stackup = '10M'
    corner = 'typical'

    for config in ('1024x32',
                   '128x116',
                   '128x256',
                   '128x32',
                   '2048x39',
                   '256x16',
                   '256x32',
                   '256x34',
                   '256x48',
                   '256x95',
                   '256x96',
                   '32x32',
                   '32x64',
                   '512x64',
                   '64x124',
                   '64x15',
                   '64x21',
                   '64x32',
                   '64x62',
                   '64x64',
                   '64x7',
                   '64x96'):

        mem_name = f'fakeram45_{config}'
        lib = Library(chip, mem_name)
        path_base = 'scgallery/libraries/freepdk45/fakeram45'
        lib.add('output', stackup, 'lef', f'{path_base}/{config}/{mem_name}.lef')
        lib.add('output', corner, 'nldm', f'{path_base}/{config}/{mem_name}.lib')

        lib.set('option', 'file', 'openroad_pdngen', f'{path_base}/pdngen.tcl')

        libs.append(lib)

    return libs
