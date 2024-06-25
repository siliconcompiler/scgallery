from os import path

from .aes import aes
from .ariane import ariane
from .black_parrot import black_parrot
from .dynamic_node import dynamic_node
from .ethmac import ethmac
from .gcd import gcd
from .heartbeat import heartbeat
from .ibex import ibex
from .jpeg import jpeg
from .mock_alu import mock_alu
from .openmsp430 import openmsp430
from .picorv32 import picorv32
from .riscv32i import riscv32i
from .spi import spi
from .swerv import swerv
from .tiny_rocket import tiny_rocket
from .uart import uart

from .caliptra import datavault, keyvault, sha512

try:
    from .zerosoc import run_flat as zerosoc_flat
    from .zerosoc import run_hierarchy as zerosoc_hierarchy
except (ImportError, ModuleNotFoundError):
    zerosoc_flat = None
    zerosoc_hierarchy = None


def __get_rules(design):
    if not design:
        return []
    rules = path.join(path.dirname(design.__file__), "rules.json")

    if path.exists(rules):
        return [rules]

    modname = design.__name__.split('.')[-1]
    rules = path.join(path.dirname(design.__file__), f"rules-{modname}.json")

    if path.exists(rules):
        return [rules]

    return []


__designs = (
    aes,
    ariane,
    black_parrot,
    datavault,
    dynamic_node,
    ethmac,
    gcd,
    heartbeat,
    ibex,
    jpeg,
    keyvault,
    mock_alu,
    openmsp430,
    picorv32,
    riscv32i,
    spi,
    swerv,
    tiny_rocket,
    uart,
    sha512
)


__name_map = {
    datavault: "caliptra-datavault",
    keyvault: "caliptra-keyvault",
    sha512: "caliptra-sha512"
}


__designs_nonstandard = {
    "zerosoc_flat": zerosoc_flat,
    "zerosoc_hierarchy": zerosoc_hierarchy
}


def all_designs():
    designs = {}
    for design in __designs:
        if not design:
            continue
        if design in __name_map:
            name = __name_map[design]
        else:
            name = design.__name__.split('.')[-1]
        rules = __get_rules(design)

        designs[name] = {
            "module": design,
            "rules": rules
        }

    for name, design in __designs_nonstandard.items():
        if not design:
            continue

        rules = __get_rules(design)
        designs[name] = {
            "module": design,
            "rules": rules
        }

    return designs


__all__ = [
    *all_designs().keys()
]


def root():
    return path.dirname(path.abspath(__file__))
