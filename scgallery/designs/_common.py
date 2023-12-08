from lambdapdk.freepdk45.libs import fakeram45
from lambdapdk.asap7.libs import fakeram7
from lambdapdk.sky130.libs import sky130sram


def register_lambdapdk(chip):
    chip.register_package_source(name='lambdapdk',
                                 path='git+https://github.com/siliconcompiler/lambdapdk.git',
                                 ref='5acea636dc29f5437434a77fa8f4d5595ce0a076')


def add_lambdapdk_memory(chip):
    pdk = chip.get('option', 'pdk')

    if pdk == 'freepdk45':
        chip.use(fakeram45)
        chip.add('option', 'ydir', 'lambdapdk/freepdk45/libs/fakeram45/lambda', package='lambdapdk')
        chip.add('asic', 'macrolib', [macro for macro in chip.getkeys('library')
                                      if macro.startswith('fakeram45_')])
    elif pdk == 'skywater130':
        chip.use(sky130sram)
        chip.add('option', 'ydir', 'lambdapdk/sky130/libs/sky130sram/lambda', package='lambdapdk')
        chip.add('asic', 'macrolib', [macro for macro in chip.getkeys('library')
                                      if macro.startswith('sky130_sram_')])
    elif pdk == 'asap7':
        chip.use(fakeram7)
        chip.add('option', 'ydir', 'lambdapdk/asap7/libs/fakeram7/lambda', package='lambdapdk')
        chip.add('asic', 'macrolib', [macro for macro in chip.getkeys('library')
                                      if macro.startswith('fakeram7_')])
