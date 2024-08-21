from ..src import make_lib
from ..src import libs


def setup(chip):
    lib = make_lib(
        chip,
        'caliptra_datavault',
        'src/datavault/rtl',
        (
            'dv_reg_pkg.sv',
            'dv_reg.sv',
            'dv_defines_pkg.sv',
            'dv.sv'
        ),
        [
            'src/datavault/rtl'
        ])
    lib.use(libs)

    return lib
