from scgallery.designs.zerosoc.zerosoc import build


def run():
    return build.build_top_flat(verify=False,
                                remote=False,
                                resume=False,
                                floorplan=False)
