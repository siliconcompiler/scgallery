from siliconcompiler import ASIC
from siliconcompiler.targets import freepdk45_demo


def nangate45(proj: ASIC):
    freepdk45_demo(proj)
