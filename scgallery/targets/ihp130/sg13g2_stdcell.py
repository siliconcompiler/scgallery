from siliconcompiler import ASICProject
from siliconcompiler.targets import ihp130_demo


def setup(proj: ASICProject):
    ihp130_demo.setup(proj)
