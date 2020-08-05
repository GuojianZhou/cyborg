# Copyright 2020 Cambricon, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


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
