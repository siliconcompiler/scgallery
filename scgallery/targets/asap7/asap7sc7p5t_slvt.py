from siliconcompiler.targets import asap7_demo


def setup(chip):
    chip.load_target(asap7_demo)
    chip.set('asic', 'logiclib', 'asap7sc7p5t_slvt')
