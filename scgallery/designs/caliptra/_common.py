import os


def __add_sources(chip, root, files):
    chip.register_package_source(name='caliptra-rtl',
                                 path='git+https://github.com/chipsalliance/caliptra-rtl.git',
                                 ref='440a21d2ce0173139273cf7261a66f490bc630f6')

    for src in files:
        chip.input(os.path.join(root, src),
                   fileset='rtl',
                   filetype='verilog',
                   package='caliptra-rtl')


def add_libs(chip):
    libs_root = os.path.join('src', 'libs', 'rtl')
    __add_sources(chip, libs_root, ('caliptra_sva.svh',
                                    'caliptra_macros.svh',
                                    'caliptra_sram.sv',
                                    'ahb_defines_pkg.sv',
                                    'caliptra_ahb_srom.sv',
                                    'apb_slv_sif.sv',
                                    'ahb_slv_sif.sv',
                                    'caliptra_icg.sv',
                                    'clk_gate.sv',
                                    'caliptra_2ff_sync.sv',
                                    'ahb_to_reg_adapter.sv'))


def add_caliptra_top_defines(chip):
    integration_root = os.path.join('src', 'integration', 'rtl')
    __add_sources(chip, integration_root, ('config_defines.svh',
                                           'caliptra_reg_defines.svh'))


def add_datavault(chip):
    datavault_root = os.path.join('src', 'datavault', 'rtl')
    __add_sources(chip, datavault_root, ('dv_reg_pkg.sv',
                                         'dv_reg.sv',
                                         'dv_defines_pkg.sv',
                                         'dv.sv'))


def add_keyvault(chip):
    datavault_root = os.path.join('src', 'keyvault', 'rtl')
    __add_sources(chip, datavault_root, ('kv_reg_pkg.sv',
                                         'kv_reg.sv',
                                         'kv_defines_pkg.sv',
                                         'kv.sv',
                                         'kv_fsm.sv',
                                         'kv_read_client.sv',
                                         'kv_write_client.sv',
                                         'kv_macros.svh'))


def add_pcrvault(chip):
    pcrvault_root = os.path.join('src', 'pcrvault', 'rtl')
    __add_sources(chip, pcrvault_root, ('pv_reg_pkg.sv',
                                        'pv_reg.sv',
                                        'pv_defines_pkg.sv',
                                        'pv.sv',
                                        'pv_macros.svh',
                                        'pv_gen_hash.sv'))


def add_sha512(chip):
    sha512_root = os.path.join('src', 'sha512', 'rtl')
    __add_sources(chip, sha512_root, ('sha512_reg_pkg.sv',
                                      'sha512_params_pkg.sv',
                                      'sha512_ctrl.sv',
                                      'sha512.sv',
                                      'sha512_core.v',
                                      'sha512_h_constants.v',
                                      'sha512_k_constants.v',
                                      'sha512_w_mem.v',
                                      'sha512_reg.sv'))
