from siliconcompiler import Chip
from lambdapdk.freepdk45.libs import fakeram45
from lambdapdk.asap7.libs import fakeram7
from lambdapdk.sky130.libs import sky130sram
from lambdapdk.gf180.libs import gf180sram

# Dictionary of lambdalib memories to process
# "pdk":
#   [(module, [libraries])]
__lambdalib_memories = {}


def register_lambdalib_memory(pdk, module):
    libs = set()

    memories = __lambdalib_memories.setdefault(pdk, [])
    if any([module == sc_module for sc_module, _ in memories]):
        return

    sc_libs = module.setup(Chip('unused'))
    if not isinstance(sc_libs, (list, tuple)):
        sc_libs = [sc_libs]

    for lib in sc_libs:
        libs.add(lib.design)

    __lambdalib_memories[pdk].append(
        (module, list(libs))
    )


register_lambdalib_memory("freepdk45", fakeram45)
register_lambdalib_memory("asap7", fakeram7)
register_lambdalib_memory("skywater130", sky130sram)
register_lambdalib_memory("gf180", gf180sram)


def add_lambdalib_memory(chip):
    pdk = chip.get('option', 'pdk')

    if pdk not in __lambdalib_memories:
        raise ValueError(f"{pdk} is not a supported pdk for lambdapdk memories")

    for module, libs in __lambdalib_memories[pdk]:
        chip.use(module)
        # Add lambdalib
        chip.add('option', 'library',
                 [lib for lib in libs if lib.startswith('lambdalib_')])

        # Add non-lambdalib
        chip.add('asic', 'macrolib',
                 [lib for lib in libs if not lib.startswith('lambdalib_')])
