from siliconcompiler import ASICProject
from siliconcompiler.targets import asap7_demo


def setup(proj: ASICProject):
    proj.load_target(asap7_demo.setup)
