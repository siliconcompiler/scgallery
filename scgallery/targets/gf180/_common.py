from lambdapdk.gf180.libs import gf180sram


def register_lambdalib(gallery):
    gallery.register_lambdalib(
        "gf180",
        "*",
        gf180sram,
        [("lambdalib_ramlib", "lambdalib_gf180sram")]
    )
