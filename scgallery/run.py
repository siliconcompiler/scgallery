import os
import shutil

from scgallery import get_image_directory

from siliconcompiler.targets import asap7_demo, freepdk45_demo, skywater130_demo

from scgallery.designs import all_designs


def __design_has_runner(design):
    return getattr(design, 'run', None) is not None


def __copy_chip_image(chip):
    jobname = chip.get('option', 'jobname')
    png = os.path.join(chip._getworkdir(),
                       f'{chip.design}.png')
    if os.path.isfile(png):
        shutil.copy(png, os.path.join(get_image_directory(), f'{chip.design}_{jobname}.png'))


def run_design(design, target):
    try:
        chip = design.setup(target=target)
    except FileNotFoundError:
        return None

    jobname = chip.get('option', 'target').split('.')[-1]
    chip.set('option', 'jobname', f"{chip.get('option', 'jobname')}_{jobname}")

    chip.set('option', 'nodisplay', True)
    chip.set('option', 'resume', True)

    try:
        chip.run()
        chip.summary()
    except Exception:
        return None

    return chip


if __name__ == "__main__":
    all_targets = (freepdk45_demo,
                   skywater130_demo,
                   asap7_demo)

    for design in all_designs().values():
        if __design_has_runner(design):
            run = getattr(design, 'run')
            try:
                chip = run()
                __copy_chip_image(chip)
            except Exception:
                pass
        else:
            for target in all_targets:
                chip = run_design(design, target)
                __copy_chip_image(chip)
