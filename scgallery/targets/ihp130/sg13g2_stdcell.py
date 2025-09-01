from siliconcompiler import ASICProject
from siliconcompiler.targets import ihp130_demo


def setup(proj: ASICProject):
    proj.load_target(ihp130_demo.setup)
