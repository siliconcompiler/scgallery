from siliconcompiler import ASICProject
from siliconcompiler.targets import skywater130_demo
from lambdapdk.sky130.libs.sky130sc import Sky130_SCHDLLLibrary


def setup(proj: ASICProject):
    proj.load_target(skywater130_demo.setup)
    proj.set_mainlib(Sky130_SCHDLLLibrary())
