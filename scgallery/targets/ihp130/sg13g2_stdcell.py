from siliconcompiler.targets import ihp130_demo
from lambdapdk.ihp130.libs import sg13g2_sram


def setup(chip):
    chip.use(ihp130_demo)


def register_lambdalib(gallery):
    gallery.register_lambdalib(
        "ihp130",
        "*",
        sg13g2_sram,
        [('lambdalib_ramlib', 'lambdalib_sg13g2_sram')]
    )
