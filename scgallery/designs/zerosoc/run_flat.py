from . import init_zerosoc


def setup():
    build = init_zerosoc()
    return build.setup_top_flat()
