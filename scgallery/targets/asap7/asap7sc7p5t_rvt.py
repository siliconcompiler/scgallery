from siliconcompiler.targets import asap7_demo
from scgallery.targets.asap7 import _common


def setup(chip):
    chip.use(asap7_demo)
    chip.set('asic', 'logiclib', 'asap7sc7p5t_rvt')
    chip.add('asic', 'logiclib', 'asap7sc7p5t_lvt')
    chip.add('asic', 'logiclib', 'asap7sc7p5t_slvt')


def register_lambdalib(gallery):
    _common.register_lambdalib(gallery)
