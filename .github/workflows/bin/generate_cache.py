import os
import sys
from pathlib import Path

from siliconcompiler import Chip
from siliconcompiler.package import path as sc_path
import lambdalib
import lambdapdk


if __name__ == "__main__":
    chip = Chip('cache')

    chip.use(lambdalib)
    for pdk in lambdapdk.get_pdks():
        chip.use(pdk)

    for lib in lambdapdk.get_libs():
        chip.use(lib)

    cwd = Path(os.getcwd())
    chip.set('option', 'cachedir', cwd / '.sc' / 'cache')

    for package in chip.getkeys('package', 'source'):
        chip.logger.info(f"Fetching {package} data source")

        try:
            sc_path(chip, package)
        except Exception as e:
            chip.logger.info(f"Failed to generate cache for {package}: {e}")
            sys.exit(1)

    sys.exit(0)
