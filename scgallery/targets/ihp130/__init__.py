from siliconcompiler import ASIC
from siliconcompiler.targets import ihp130_demo


def sg13g2_stdcell(proj: ASIC):
    ihp130_demo(proj)
