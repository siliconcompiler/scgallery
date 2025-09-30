from siliconcompiler import ASIC
from siliconcompiler.targets import skywater130_demo
from lambdapdk.sky130.libs.sky130sc import Sky130_SCHDLibrary
from lambdapdk.sky130.libs.sky130sc import Sky130_SCHDLLLibrary


def sky130hd(proj: ASIC):
    skywater130_demo(proj)
    proj.set_mainlib(Sky130_SCHDLibrary())


def sky130hdll(proj: ASIC):
    skywater130_demo(proj)
    proj.set_mainlib(Sky130_SCHDLLLibrary())
