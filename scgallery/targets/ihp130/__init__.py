from siliconcompiler import ASICProject
from siliconcompiler.targets import ihp130_demo


def sg13g2_stdcell(proj: ASICProject):
    ihp130_demo(proj)
