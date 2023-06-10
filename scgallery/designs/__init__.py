from .sha3 import sha3
from .aes import aes
from .ethmac import ethmac
from .jpeg import jpeg
from .uart import uart

from .zerosoc import run_flat as zerosoc_flat


def all_designs():
    return {
        "aes": aes,
        "sha3": sha3,
        "ethmac": ethmac,
        "jpeg": jpeg,
        "uart": uart,
        "zerosoc_flat": zerosoc_flat
    }


__all__ = [
    *all_designs().keys()
]
