from . import init_zerosoc


def setup():
    build = init_zerosoc()
    return build._setup_top_flat()
