from siliconcompiler.targets import gf180_demo
from scgallery.targets.gf180 import _common


def setup(chip):
    chip.use(gf180_demo)
    chip.set('asic', 'logiclib', 'gf180mcu_fd_sc_mcu9t5v0')


def register_lambdalib(gallery):
    _common.register_lambdalib(gallery)
