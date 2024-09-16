from siliconcompiler.targets import freepdk45_demo


def setup(chip):
    chip.use(freepdk45_demo)
    chip.set('asic', 'logiclib', 'faux')


def register_lambdalib(gallery):
    pass
