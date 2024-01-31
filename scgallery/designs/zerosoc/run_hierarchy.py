from . import init_zerosoc


def runtime_setup(gallery):
    build = init_zerosoc()
    core_chip = build.build_core(remote=False,
                                 verify=False,
                                 resume=gallery.is_resume,
                                 floorplan=False)
    return build.setup_top_hier(core_chip)
