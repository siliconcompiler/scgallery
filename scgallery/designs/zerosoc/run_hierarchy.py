from scgallery.designs.zerosoc.zerosoc import build


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
