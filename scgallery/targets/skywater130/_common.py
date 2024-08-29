from lambdapdk.sky130.libs import sky130sram


def register_lambdalib(gallery):
    gallery.register_lambdalib(
        "skywater130",
        "*",
        sky130sram,
        [("lambdalib_ramlib", "lambdalib_sky130sram")]
    )
