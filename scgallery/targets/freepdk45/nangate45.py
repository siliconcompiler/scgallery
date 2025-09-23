from siliconcompiler import ASICProject
from siliconcompiler.targets import freepdk45_demo


def setup(proj: ASICProject):
    freepdk45_demo.setup(proj)
