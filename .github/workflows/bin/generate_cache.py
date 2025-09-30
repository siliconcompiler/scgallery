import os
import sys
from pathlib import Path

from siliconcompiler import ASIC
from lambdapdk.asap7 import ASAP7PDK
from lambdapdk.freepdk45 import FreePDK45PDK
from lambdapdk.gf180 import GF180_5LM_1TM_9K_9t
from lambdapdk.ihp130 import IHP130PDK
from lambdapdk.sky130 import Sky130PDK


if __name__ == "__main__":
    proj = ASIC("cache")

    proj.set('option', 'cachedir', Path(os.getcwd()) / '.sc' / 'cache')

    proj.add_dep(ASAP7PDK())
    proj.add_dep(FreePDK45PDK())
    proj.add_dep(GF180_5LM_1TM_9K_9t())
    proj.add_dep(IHP130PDK())
    proj.add_dep(Sky130PDK())

    proj.check_filepaths([("option", "builddir")])

    sys.exit(0)
