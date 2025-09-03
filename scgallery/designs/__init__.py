from os import path

from .aes.aes import AESDesign
from .black_parrot.black_parrot import BlackParrotDesign
from .blinky.blinky import BlinkyDesign
from .caliptra.datavault import DataVault
from .caliptra.keyvault import KeyVault
from .caliptra.sha512 import SHA512
from .cva6.cva6 import CVA6Design
from .darkriscv.darkriscv import DarkSOCVDesign
from .dynamic_node.dynamic_node import DynamicNodeDesign
from .ethmac.ethmac import EthmacDesign
from .fazyrv.fazyrv import FazyRVDesign
from .gcd.gcd import GCDDesign
from .heartbeat.heartbeat import HeartbeatDesign
from .ibex.ibex import IBEXDesign
from .jpeg.jpeg import JPEGDesign
from .mock_alu.mock_alu import MockALUDesign
from .openmsp430.openmsp430 import OpenMSP430Design
from .picorv32.picorv32 import PicoRV32Design
from .qerv.qerv import QERVDesign
from .riscv32i.riscv32i import Riscv32iDesign
from .serv.serv import SERVDesign
from .spi.spi import SPIDesign
from .swerv.swerv import SwervDesign
from .tiny_rocket.tiny_rocket import TinyRocketDesign
from .uart.uart import UARTDesign

__designs = (
    AESDesign,
    BlackParrotDesign,
    BlinkyDesign,
    DataVault,
    KeyVault,
    SHA512,
    CVA6Design,
    DarkSOCVDesign,
    DynamicNodeDesign,
    EthmacDesign,
    FazyRVDesign,
    GCDDesign,
    HeartbeatDesign,
    IBEXDesign,
    JPEGDesign,
    MockALUDesign,
    OpenMSP430Design,
    PicoRV32Design,
    QERVDesign,
    Riscv32iDesign,
    SERVDesign,
    SPIDesign,
    SwervDesign,
    TinyRocketDesign,
    UARTDesign
)


__designs_nonstandard = {
}


def all_designs():
    designs = {}
    for design in __designs:
        if not design:
            continue
        name = design().name

        designs[name] = design

    for name, design in __designs_nonstandard.items():
        if not design:
            continue

        designs[name] = design

    return designs


__all__ = [
    *all_designs().keys()
]


def root():
    return path.dirname(path.abspath(__file__))
