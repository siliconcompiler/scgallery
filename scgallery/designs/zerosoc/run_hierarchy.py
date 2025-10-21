from . import init_zerosoc


gallery_needs_target = False


def runtime_setup(gallery):
    build = init_zerosoc()
    core_chip = build.build_core(
        remote=False, verify=False, resume=not gallery.is_clean, floorplan=False
    )
    return build._setup_top_hier(core_chip)
