import os
import sys
from pathlib import Path

from siliconcompiler import ASIC
from lambdapdk.asap7 import ASAP7PDK
from lambdapdk.freepdk45 import FreePDK45PDK
from lambdapdk.gf180 import GF180_5LM_1TM_9K_9t
from lambdapdk.ihp130 import IHP130PDK
from lambdapdk.sky130 import Sky130PDK
from lambdapdk.gt2n import GT2NPDK
from lambdapdk.icsprout55 import ICS55PDK
from lambdapdk.icsprout55.libs.stdcells import (
    ICS55StdCellRVT,
    ICS55StdCellHVT,
    ICS55StdCellLVT,
)


if __name__ == "__main__":
    proj = ASIC("cache")

    proj.option.set_cachedir(Path(os.getcwd()) / '.sc' / 'cache')

    proj.add_dep(ASAP7PDK())
    proj.add_dep(FreePDK45PDK())
    proj.add_dep(GF180_5LM_1TM_9K_9t())
    proj.add_dep(IHP130PDK())
    proj.add_dep(Sky130PDK())
    proj.add_dep(GT2NPDK())
    proj.add_dep(ICS55PDK())

    # ICsprout55 vendors nothing: the liberty and GDS live in release assets
    # reached through dataroots declared on the libraries, not on the PDK, so
    # caching ICS55PDK alone leaves every design job to fetch them itself.
    # ics55_demo loads all three Vt flavours.
    proj.add_dep(ICS55StdCellRVT())
    proj.add_dep(ICS55StdCellHVT())
    proj.add_dep(ICS55StdCellLVT())

    proj.check_filepaths([("option", "builddir")])

    sys.exit(0)
