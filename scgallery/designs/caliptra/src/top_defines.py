from ..src import make_lib


def setup():
    lib = make_lib(
        'caliptra_top_defines',
        'src/integration/rtl',
        [],
        [
            'src/integration/rtl'
        ])

    return lib
