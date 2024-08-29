from ..src import make_lib
from ..src import libs


def setup():
    lib = make_lib(
        'caliptra_pcrvault',
        'src/pcrvault/rtl',
        (
            'pv_reg_pkg.sv',
            'pv_reg.sv',
            'pv_defines_pkg.sv',
            'pv.sv',
            'pv_gen_hash.sv'
        ),
        [
            'src/pcrvault/rtl'
        ])
    lib.use(libs)

    return lib
