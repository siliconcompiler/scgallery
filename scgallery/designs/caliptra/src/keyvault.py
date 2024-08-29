from ..src import make_lib
from ..src import libs


def setup():
    lib = make_lib(
        'caliptra_keyvault',
        'src/keyvault/rtl',
        (
            'kv_reg_pkg.sv',
            'kv_reg.sv',
            'kv_defines_pkg.sv',
            'kv.sv',
            'kv_fsm.sv',
            'kv_read_client.sv',
            'kv_write_client.sv'
        ),
        [
            'src/keyvault/rtl'
        ])
    lib.use(libs)

    return lib
