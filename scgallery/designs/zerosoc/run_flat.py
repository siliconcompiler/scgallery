from . import init_zerosoc


def run():
    build = init_zerosoc()
    return build.build_top_flat(verify=False,
                                remote=False,
                                resume=False,
                                floorplan=False)
