from . import init_zerosoc
init_zerosoc()
from scgallery.designs.zerosoc.zerosoc import build  # noqa E402


def run():
    return build.build_top_flat(verify=False,
                                remote=False,
                                resume=False,
                                floorplan=False)
