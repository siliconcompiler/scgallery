from ..src import make_lib
from ..src import pcrvault, keyvault


def setup():
    lib = make_lib(
        'caliptra_sha512',
        'src/sha512/rtl',
        (
            'sha512_reg_pkg.sv',
            'sha512_params_pkg.sv',
            'sha512_ctrl.sv',
            'sha512.sv',
            'sha512_core.v',
            'sha512_h_constants.v',
            'sha512_k_constants.v',
            'sha512_w_mem.v',
            'sha512_reg.sv'
        ))
    lib.use(pcrvault)
    lib.use(keyvault)

    return lib
