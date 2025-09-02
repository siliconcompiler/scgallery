from os import path

from .aes.aes import AESDesign
from .blinky.blinky import BlinkyDesign
from .darkriscv.darkriscv import DarkSOCVDesign
from .dynamic_node.dynamic_node import DynamicNodeDesign
from .ethmac.ethmac import EthmacDesign
from .fazyrv.fazyrv import FazyRVDesign
from .gcd.gcd import GCDDesign
from .heartbeat.heartbeat import HeartbeatDesign
from .ibex.ibex import IBEXDesign
from .jpeg.jpeg import JPEGDesign
from .openmsp430.openmsp430 import OpenMSP430Design
from .picorv32.picorv32 import PicoRV32Design

__designs = (
    AESDesign,
    BlinkyDesign,
    DarkSOCVDesign,
    DynamicNodeDesign,
    EthmacDesign,
    FazyRVDesign,
    GCDDesign,
    HeartbeatDesign,
    IBEXDesign,
    JPEGDesign,
    OpenMSP430Design,
    PicoRV32Design
)


__name_map = {
}


__designs_nonstandard = {
}


def all_designs():
    designs = {}
    for design in __designs:
        if not design:
            continue
        if design in __name_map:
            name = __name_map[design]
        else:
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
