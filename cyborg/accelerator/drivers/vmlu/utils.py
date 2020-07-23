"""
Utils for VMLU driver.
"""

import glob
import re


VENDORS = ["cambricon"]  

SYS_VMLU_PATH = "/sys/class/cambricon"
VENDORS_PATTERN = re.compile("|".join(["(%s)" % v for v in VENDORS]))


def discover_vendors():
    vendors = set()
    for p in glob.glob1(SYS_VMLU_PATH, "*"):
        m = VENDORS_PATTERN.match(p)
        if m:
            vendors.add(m.group())
    return list(vendors)

