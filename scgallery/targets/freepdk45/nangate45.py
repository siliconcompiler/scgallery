from siliconcompiler import ASICProject
from siliconcompiler.targets import freepdk45_demo


def setup(proj: ASICProject):
    proj.load_target(freepdk45_demo.setup)
