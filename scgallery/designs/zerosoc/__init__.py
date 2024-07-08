import importlib
import os
import sys

from siliconcompiler import Chip
from siliconcompiler import package


def register_zerosoc(chip):
    chip.register_source(name='zerosoc_data',
                         path='git+https://github.com/siliconcompiler/zerosoc',
                         ref='c770a00f197b0f5b388adb8dce34b9ba22c54039')


def init_zerosoc():
    chip = Chip('zerosoc')
    register_zerosoc(chip)
    # Touch zerosoc to ensure download
    zerosoc = package.path(chip, 'zerosoc_data')
    sys_path = os.path.dirname(zerosoc)
    package_name = os.path.basename(zerosoc)

    for path in [sys_path, zerosoc]:
        if path not in sys.path:
            sys.path.append(path)

    return importlib.import_module(f'{package_name}.build')
