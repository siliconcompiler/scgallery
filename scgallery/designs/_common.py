from lambdapdk.freepdk45.libs import fakeram45
from lambdapdk.asap7.libs import fakeram7
from lambdapdk.sky130.libs import sky130sram


def register_lambdapdk(chip):
    chip.register_package_source(name='lambdapdk',
                                 path='git+https://github.com/siliconcompiler/lambdapdk.git',
                                 ref='5acea636dc29f5437434a77fa8f4d5595ce0a076')


def add_lambdapdk_memory(chip):
    pdk = chip.get('option', 'pdk')

    macros = set(chip.getkeys('library'))
    if pdk == 'freepdk45':
        chip.use(fakeram45)
    elif pdk == 'skywater130':
        chip.use(sky130sram)
    elif pdk == 'asap7':
        chip.use(fakeram7)
    else:
        raise ValueError(f"{pdk} is not a supported pdk for lambdapdk memories")

    # Add memory macros to macrolib
    new_macros = set(chip.getkeys('library'))
    chip.add('asic', 'macrolib', list(new_macros.difference(macros)))
