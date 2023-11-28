from . import init_zerosoc


def run():
    build = init_zerosoc()
    core_chip = build.build_core(remote=False,
                                 verify=False,
                                 resume=False,
                                 floorplan=False)
    return build.build_top(core_chip=core_chip,
                           remote=False,
                           verify=False,
                           resume=False,
                           floorplan=False)
