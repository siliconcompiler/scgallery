from siliconcompiler.targets import freepdk45_demo
from lambdapdk.freepdk45.libs import fakeram45


def setup(chip):
    chip.use(freepdk45_demo)


def register_lambdalib(gallery):
    gallery.register_lambdalib(
        "freepdk45",
        "*",
        fakeram45,
        [('lambdalib_ramlib', 'lambdalib_fakeram45')]
    )
