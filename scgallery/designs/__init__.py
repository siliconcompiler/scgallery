from .sha3 import sha3
from .aes import aes
from .gcd import gcd
from .ethmac import ethmac
from .jpeg import jpeg
from .uart import uart
from .heartbeat import heartbeat

from .zerosoc import run_flat as zerosoc_flat
from .zerosoc import run_hierarchy as zerosoc_hierarchy


def all_designs():
    return {
        "aes": aes,
        "gcd": gcd,
        "sha3": sha3,
        "ethmac": ethmac,
        "jpeg": jpeg,
        "uart": uart,
        "heartbeat": heartbeat,
        "zerosoc_flat": zerosoc_flat,
        "zerosoc_hierarchy": zerosoc_hierarchy
    }


__all__ = [
    *all_designs().keys()
]
