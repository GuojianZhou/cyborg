
"""
Cyborg VMLU driver implementation.
"""

from cyborg.accelerator.drivers.vmlu import utils


VENDOR_MAPS = {"0xcabc": "cambricon"}


class VMLUDriver(object):
    """Base class for VMLU drivers.
       This is just a virtual MLU drivers interface.
       Vendor should implement their specific drivers.
    """

    @classmethod
    def create(cls, vendor, *args, **kwargs):
        for sclass in cls.__subclasses__():
            vendor = VENDOR_MAPS.get(vendor, vendor)
            if vendor == sclass.VENDOR:
                return sclass(*args, **kwargs)
        raise LookupError("Not find the VMLU driver for vendor %s" % vendor)

    def __init__(self, *args, **kwargs):
        pass

    def discover(self):
        raise NotImplementedError()

    @classmethod
    def discover_vendors(cls):
        return utils.discover_vendors()
