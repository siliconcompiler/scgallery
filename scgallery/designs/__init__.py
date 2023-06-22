from os import path

from .aes import aes
from .black_parrot import black_parrot
from .dynamic_node import dynamic_node
from .ethmac import ethmac
from .gcd import gcd
from .heartbeat import heartbeat
from .ibex import ibex
from .jpeg import jpeg
from .microwatt import microwatt
from .riscv32i import riscv32i
from .sha3 import sha3
from .swerv import swerv
from .tiny_rocket import tiny_rocket
from .uart import uart

from .zerosoc import run_flat as zerosoc_flat
from .zerosoc import run_hierarchy as zerosoc_hierarchy


def __get_rules(design):
    rules = path.join(path.dirname(design.__file__), "rules.json")
    if path.exists(rules):
        return [rules]
    return []


def all_designs():
    return {
        "aes": {
            "module": aes,
            "rules": __get_rules(aes)},
        "black_parrot": {
            "module": black_parrot,
            "rules": __get_rules(black_parrot)},
        "dynamic_node": {
            "module": dynamic_node,
            "rules": __get_rules(dynamic_node)},
        "ethmac": {
            "module": ethmac,
            "rules": __get_rules(ethmac)},
        "gcd": {
            "module": gcd,
            "rules": __get_rules(gcd)},
        "heartbeat": {
            "module": heartbeat,
            "rules": __get_rules(heartbeat)},
        "ibex": {
            "module": ibex,
            "rules": __get_rules(ibex)},
        "jpeg": {
            "module": jpeg,
            "rules": __get_rules(jpeg)},
        "microwatt": {
            "module": microwatt,
            "rules": __get_rules(microwatt)},
        "riscv32i": {
            "module": riscv32i,
            "rules": __get_rules(riscv32i)},
        "sha3": {
            "module": sha3,
            "rules": __get_rules(sha3)},
        "swerv": {
            "module": swerv,
            "rules": __get_rules(swerv)},
        "tiny_rocket": {
            "module": tiny_rocket,
            "rules": __get_rules(tiny_rocket)},
        "uart": {
            "module": uart,
            "rules": __get_rules(uart)},
        "zerosoc_flat": {
            "module": zerosoc_flat,
            "rules": __get_rules(zerosoc_flat)},
        "zerosoc_hierarchy": {
            "module": zerosoc_hierarchy,
            "rules": __get_rules(zerosoc_hierarchy)}
    }


__all__ = [
    *all_designs().keys()
]
