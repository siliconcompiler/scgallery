import os
from siliconcompiler import Library


def __register(lib):
    lib.register_source(
        name='caliptra-rtl',
        path='git+https://github.com/chipsalliance/caliptra-rtl.git',
        ref='v1.0')


def __add_sources(lib, root, files):
    for src in files:
        lib.input(os.path.join(root, src))


def __make_lib(chip, name, root, files, idirs=None):
    lib = Library(chip, name, package='caliptra-rtl')
    __register(lib)

    __add_sources(lib, root, files)

    if idirs:
        lib.add('option', 'idir', idirs)

    return lib


def setup(chip):
    libs_root = os.path.join('src', 'libs', 'rtl')
    integration_root = os.path.join('src', 'integration', 'rtl')
    datavault_root = os.path.join('src', 'datavault', 'rtl')
    keyvault_root = os.path.join('src', 'keyvault', 'rtl')
    pcrvault_root = os.path.join('src', 'pcrvault', 'rtl')
    sha512_root = os.path.join('src', 'sha512', 'rtl')
    return [
        __make_lib(
            chip,
            'caliptra_libs',
            libs_root,
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
                libs_root
            ]),
        __make_lib(
            chip,
            'caliptra_top_defines',
            integration_root,
            [],
            [
                integration_root
            ]),
        __make_lib(
            chip,
            'caliptra_datavault',
            datavault_root,
            (
                'dv_reg_pkg.sv',
                'dv_reg.sv',
                'dv_defines_pkg.sv',
                'dv.sv'
            ),
            [
                datavault_root
            ]),
        __make_lib(
            chip,
            'caliptra_keyvault',
            keyvault_root,
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
                keyvault_root
            ]),
        __make_lib(
            chip,
            'caliptra_pcrvault',
            pcrvault_root,
            (
                'pv_reg_pkg.sv',
                'pv_reg.sv',
                'pv_defines_pkg.sv',
                'pv.sv',
                'pv_gen_hash.sv'
            ),
            [
                pcrvault_root
            ]),
        __make_lib(
            chip,
            'caliptra_sha512',
            sha512_root,
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
    ]
