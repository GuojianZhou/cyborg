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
Cyborg Cambricon VMLU driver implementation.
"""
import subprocess

from oslo_concurrency import processutils
from oslo_log import log as logging

from cyborg.accelerator.drivers.vmlu.base import VMLUDriver
from cyborg.accelerator.drivers.vmlu.cambricon import sysinfo
from cyborg.common import exception
import cyborg.privsep

LOG = logging.getLogger(__name__)


class cambriconVMLUDriver(VMLUDriver):
    """Base class for VMLU drivers.
       This is just virtual MLU drivers interface.
       Vedor should implement their specific drivers.
    """
    VENDOR = "cambricon"

    def __init__(self, *args, **kwargs):
        pass

    def discover(self):
        return sysinfo.vmlu_tree()

