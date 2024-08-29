from siliconcompiler.targets import skywater130_demo
from scgallery.targets.skywater130 import _common


def setup(chip):
    chip.use(skywater130_demo)

    chip.set('asic', 'logiclib', 'sky130hd')


def register_lambdalib(gallery):
    _common.register_lambdalib(gallery)
