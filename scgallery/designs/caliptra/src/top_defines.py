from ..src import make_lib


def setup(chip):
    lib = make_lib(
        chip,
        'caliptra_top_defines',
        'src/integration/rtl',
        [],
        [
            'src/integration/rtl'
        ])

    return lib
