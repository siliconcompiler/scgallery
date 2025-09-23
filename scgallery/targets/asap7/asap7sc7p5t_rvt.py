from siliconcompiler import ASICProject
from siliconcompiler.targets import asap7_demo


def setup(proj: ASICProject):
    asap7_demo.setup(proj)
