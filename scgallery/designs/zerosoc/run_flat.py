from . import init_zerosoc


gallery_needs_target = False


def setup():
    build = init_zerosoc()
    return build._setup_top_flat()
