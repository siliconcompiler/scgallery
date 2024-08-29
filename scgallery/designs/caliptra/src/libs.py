from ..src import make_lib
from ..src import top_defines


def setup():
    lib = make_lib(
        'caliptra_libs',
        'src/libs/rtl',
        (
            'caliptra_sram.sv',
            'ahb_defines_pkg.sv',
            'caliptra_ahb_srom.sv',
            'apb_slv_sif.sv',
            'ahb_slv_sif.sv',
            'caliptra_icg.sv',
            'clk_gate.sv',
            'caliptra_2ff_sync.sv',
            'ahb_to_reg_adapter.sv'
        ),
        [
            'src/libs/rtl'
        ])
    lib.use(top_defines)

    return lib
