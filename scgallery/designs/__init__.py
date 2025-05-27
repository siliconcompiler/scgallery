from os import path

from .aes import aes
from .black_parrot import black_parrot
from .blinky import blinky
from .cva6 import cva6
from .darkriscv import darkriscv
from .dynamic_node import dynamic_node
from .ethmac import ethmac
from .fazyrv import fazyrv
from .gcd import gcd
from .heartbeat import heartbeat
from .ibex import ibex
from .jpeg import jpeg
from .microwatt import microwatt
from .mock_alu import mock_alu
from .openmsp430 import openmsp430
from .picorv32 import picorv32
from .riscv32i import riscv32i
from .qerv import qerv
from .serv import serv
from .spi import spi
from .swerv import swerv
from .tiny_rocket import tiny_rocket
from .wally import wally
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
    black_parrot,
    blinky,
    cva6,
    darkriscv,
    datavault,
    dynamic_node,
    ethmac,
    fazyrv,
    gcd,
    heartbeat,
    ibex,
    jpeg,
    keyvault,
    microwatt,
    mock_alu,
    openmsp430,
    picorv32,
    qerv,
    riscv32i,
    serv,
    spi,
    swerv,
    tiny_rocket,
    wally,
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
