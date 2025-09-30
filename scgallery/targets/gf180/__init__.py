from siliconcompiler import ASIC
from siliconcompiler.targets import gf180_demo
from lambdapdk.gf180 import GF180_5LM_1TM_9K_7t
from lambdapdk.gf180 import GF180_5LM_1TM_9K_9t
from lambdapdk.gf180.libs.gf180mcu import GF180_MCU_7T_5LMLibrary
from lambdapdk.gf180.libs.gf180mcu import GF180_MCU_9T_5LMLibrary
from lambdapdk.gf180.libs.gf180sram import GF180Lambdalib_SinglePort


def gf180mcu_fd_sc_mcu7t5v0(proj: ASIC):
    gf180_demo(proj)
    proj.unset("asic", "asiclib")
    proj.set_pdk(GF180_5LM_1TM_9K_7t())
    proj.set_mainlib(GF180_MCU_7T_5LMLibrary())

    # 5. Assign Lambdalib aliases
    GF180Lambdalib_SinglePort.alias(proj)


def gf180mcu_fd_sc_mcu9t5v0(proj: ASIC):
    gf180_demo(proj)
    proj.unset("asic", "asiclib")
    proj.set_pdk(GF180_5LM_1TM_9K_9t())
    proj.set_mainlib(GF180_MCU_9T_5LMLibrary())

    # 5. Assign Lambdalib aliases
    GF180Lambdalib_SinglePort.alias(proj)
