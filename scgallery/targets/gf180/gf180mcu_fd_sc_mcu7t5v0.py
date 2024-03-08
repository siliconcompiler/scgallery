from siliconcompiler.targets import gf180_demo


def setup(chip):
    chip.load_target(gf180_demo)
    chip.set('asic', 'logiclib', 'gf180mcu_fd_sc_mcu7t5v0')
