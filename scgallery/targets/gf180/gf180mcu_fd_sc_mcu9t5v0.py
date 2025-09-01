from siliconcompiler import ASICProject
from siliconcompiler.targets import gf180_demo
from lambdapdk.gf180 import GF180_5LM_1TM_9K_9t
from lambdapdk.gf180.libs.gf180mcu import GF180_MCU_9T_5LMLibrary


def setup(proj: ASICProject):
    proj.load_target(gf180_demo.setup)
    proj.unset("asic", "asiclib")
    proj.set_pdk(GF180_5LM_1TM_9K_9t())
    proj.set_mainlib(GF180_MCU_9T_5LMLibrary())
