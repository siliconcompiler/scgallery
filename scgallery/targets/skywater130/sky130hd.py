from siliconcompiler import ASICProject
from siliconcompiler.targets import skywater130_demo
from lambdapdk.sky130.libs.sky130sc import Sky130_SCHDLibrary


def setup(proj: ASICProject):
    skywater130_demo.setup(proj)
    proj.set_mainlib(Sky130_SCHDLibrary())
