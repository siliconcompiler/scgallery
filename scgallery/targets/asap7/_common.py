from lambdapdk.asap7.libs import fakeram7


def register_lambdalib(gallery):
    gallery.register_lambdalib(
        "asap7",
        "*",
        fakeram7,
        [("lambdalib_ramlib", "lambdalib_fakeram7")]
    )
