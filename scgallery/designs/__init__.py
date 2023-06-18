from .aes import aes
from .black_parrot import black_parrot
from .dynamic_node import dynamic_node
from .ethmac import ethmac
from .gcd import gcd
from .heartbeat import heartbeat
from .ibex import ibex
from .jpeg import jpeg
# from .microwatt import microwatt
from .riscv32i import riscv32i
from .sha3 import sha3
from .swerv import swerv
from .tiny_rocket import tiny_rocket
from .uart import uart

from .zerosoc import run_flat as zerosoc_flat
from .zerosoc import run_hierarchy as zerosoc_hierarchy


def all_designs():
    return {
        "aes": aes,
        "black_parrot": black_parrot,
        "dynamic_node": dynamic_node,
        "ethmac": ethmac,
        "gcd": gcd,
        "heartbeat": heartbeat,
        "ibex": ibex,
        "jpeg": jpeg,
        # "microwatt": microwatt,
        "riscv32i": riscv32i,
        "sha3": sha3,
        "swerv": swerv,
        "tiny_rocket": tiny_rocket,
        "uart": uart,
        "zerosoc_flat": zerosoc_flat,
        "zerosoc_hierarchy": zerosoc_hierarchy
    }


__all__ = [
    *all_designs().keys()
]
