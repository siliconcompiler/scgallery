from . import init_zerosoc
init_zerosoc()
from scgallery.designs.zerosoc.zerosoc import build  # noqa E402


def run():
    core_chip = build.build_core(remote=False,
                                 verify=False,
                                 resume=False,
                                 floorplan=False)
    return build.build_top(core_chip=core_chip,
                           remote=False,
                           verify=False,
                           resume=False,
                           floorplan=False)
