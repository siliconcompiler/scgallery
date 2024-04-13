import importlib
import os
import sys

from siliconcompiler import Chip
from siliconcompiler import package


def register_zerosoc(chip):
    chip.register_package_source(name='zerosoc_data',
                                 path='git+https://github.com/siliconcompiler/zerosoc',
                                 ref='6ebf9cde97eba266c53fbe55222cf9f07f8172c1')


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
