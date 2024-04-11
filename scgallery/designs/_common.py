from lambdapdk.freepdk45.libs import fakeram45
from lambdapdk.asap7.libs import fakeram7
from lambdapdk.sky130.libs import sky130sram
from lambdapdk.gf180.libs import gf180sram


def add_lambdapdk_memory(chip):
    pdk = chip.get('option', 'pdk')

    macros = set(chip.getkeys('library'))
    if pdk == 'freepdk45':
        chip.use(fakeram45)
        chip.add('option', 'library', 'lambdalib_fakeram45')
    elif pdk == 'skywater130':
        chip.use(sky130sram)
        chip.add('option', 'library', 'lambdalib_sky130sram')
    elif pdk == 'asap7':
        chip.use(fakeram7)
        chip.add('option', 'library', 'lambdalib_fakeram7')
    elif pdk == 'gf180':
        chip.use(gf180sram)
        chip.add('option', 'library', 'lambdalib_gf180sram')
    else:
        raise ValueError(f"{pdk} is not a supported pdk for lambdapdk memories")

    # Add memory macros to macrolib
    new_macros = set([lib for lib in chip.getkeys('library') if 'lambdalib' not in lib])
    chip.add('asic', 'macrolib', list(new_macros.difference(macros)))
