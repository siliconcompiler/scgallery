from siliconcompiler import ASICProject
from siliconcompiler.targets import freepdk45_demo


def nangate45(proj: ASICProject):
    freepdk45_demo(proj)
