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
Cyborg cambricon VMLU driver implementation.
"""

import glob
import os
import re

from oslo_serialization import jsonutils

from cyborg.accelerator.common import utils
from cyborg.common import constants
from cyborg.objects.driver_objects import driver_attach_handle
from cyborg.objects.driver_objects import driver_attribute
from cyborg.objects.driver_objects import driver_controlpath_id
from cyborg.objects.driver_objects import driver_deployable
from cyborg.objects.driver_objects import driver_device

PCI_DEVICES_PATH = "/sys/bus/pci/devices"
PCI_DEVICES_PATH_PATTERN = "/sys/bus/pci/devices/*"

KNOWN_VMLUS = [("0xcabc", "0x0270"), ("0xcabc", "0x0290"),("0xcabc", "0x0271"), ]

CAMBRICON_VMLU_DEV_PREFIX = "cambricon_dev"
SYS_VMLU = "/sys/class/cambricon"
DEVICE = "device"
PF = "physfn"
VF = "virtfn*"
BDF_PATTERN = re.compile(
    r"^[a-fA-F\d]{4}:[a-fA-F\d]{2}:[a-fA-F\d]{2}\.[a-fA-F\d]$")

DEVICE_FILE_MAP = {"vendor": "vendor",
                   "device": "product_id"}
DEVICE_FILE_HANDLER = {}
DEVICE_EXPOSED = ["vendor", "device"]

PRODUCT_MAP = {"0x0270": "MLU270", "0x0290": "MLU290", "0x0271": "VMLU270", "0x0291": "VMLU290", "0x0201": "VMLU270"}

DRIVER_NAME = "cambricon"


def read_line(filename):
    with open(filename) as f:
        return f.readline().strip()


def is_vmlu(p):
    infos = (read_line(os.path.join(p, "vendor")),
             read_line(os.path.join(p, "device")))
    if infos in KNOWN_VMLUS:
        return os.path.realpath(p)


def link_real_path(p):
    return os.path.realpath(
        os.path.join(os.path.dirname(p), os.readlink(p)))


def find_vmlus_by_know_list():
    return filter(
        lambda p: (
            read_line(os.path.join(p, "vendor")),
            read_line(os.path.join(p, "device"))
        ) in KNOWN_VMLUS,
        glob.glob(PCI_DEVICES_PATH_PATTERN))


def get_link_targets(links):
    return map(
        lambda p:
            os.path.realpath(
                os.path.join(os.path.dirname(p), os.readlink(p))),
        links)


def all_vmlus():
    # glob.glob1("/sys/class/cambricon", "*")
    return set(get_link_targets(find_vmlus_by_know_list())) | set(
        map(lambda p: p.rsplit("/", 2)[0],
            get_link_targets(glob.glob(os.path.join(SYS_VMLU, "*")))))


def all_vf_vmlus():
    return [dev.rsplit("/", 2)[0] for dev in
            glob.glob(os.path.join(SYS_VMLU, "*/device/physfn"))]


def all_pfs_have_vf():
    return list(filter(lambda p: glob.glob(os.path.join(p, "virtfn0")),
                all_vmlus()))


def target_symbolic_map():
    maps = {}
    for f in glob.glob(os.path.join(SYS_VMLU, "*/device")):
        maps[os.path.realpath(f)] = os.path.dirname(f)
    return maps


def bdf_path_map():
    return dict(map(lambda f: (os.path.basename(f), f), all_vmlus()))


def all_vfs_in_pf_vmlus(pf_path):
    return get_link_targets(
        glob.glob(os.path.join(pf_path, "virtfn*")))


def all_pf_vmlus():
    return filter(lambda p: glob.glob(os.path.join(p, "sriov_totalvfs")),
                  all_vmlus())


def is_vf(path):
    return True if (
        glob.glob(os.path.join(path, "device/physfn")) or
        glob.glob(os.path.join(path, "physfn"))) else False


def find_pf_by_vf(path):
    if glob.glob(os.path.join(path, "physfn")):
        return link_real_path(os.path.join(path, "physfn"))


def is_bdf(bdf):
    return True if BDF_PATTERN.match(bdf) else False


def get_bdf_by_path(path):
    bdf = os.path.basename(path)
    if is_bdf(bdf):
        return bdf
    return os.path.basename(os.readlink(os.path.join(path, "device")))


def split_bdf(bdf):
    return ["0x" + v for v in bdf.replace(".", ":").rsplit(":")[1:]]


def get_pf_bdf(bdf):
    paths = glob.glob0(PCI_DEVICES_PATH, bdf)
    if paths:
        p0 = paths[0]
        path = find_pf_by_vf(p0) if is_vf(p0) else p0
        return get_bdf_by_path(path)
    return bdf


def get_traits(product_id, fun_id, vf=True):
    """Generate traits for devices.
    : param product_id: product id of PF/VF, for example, "0x0270".
    : param vf: True if device_name is a VF, otherwise False.
    """

    traits = []
    if not vf:
        traits.append("CUSTOM_VMLU_CAMBRICON")
        traits.append("CUSTOM_VMLU_CAMBRICON_" + PRODUCT_MAP.get(product_id))
    else:
        l = "CUSTOM_VMLU_FUNCTION_ID_CAMBRICON_" + fun_id.upper()
        traits.append(l)
    return {"traits": traits}


def vmlu_device(path):
    infos = {}

    # NOTE "In 3.x, os.path.walk is removed in favor of os.walk."
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            if filename in DEVICE_EXPOSED:
                key = DEVICE_FILE_MAP.get(filename) or filename
                if key in DEVICE_FILE_HANDLER and callable(
                    DEVICE_FILE_HANDLER(key)):
                    infos[key] = DEVICE_FILE_HANDLER(key)(
                        os.path.join(dirpath, filename))
                else:
                    infos[key] = read_line(os.path.join(dirpath, filename))
    return infos


def vmlu_tree():
    def gen_vmlu_infos(path, vf=True):
        bdf = get_bdf_by_path(path)
        fun_id = [ v for v in bdf.replace(".", ":").rsplit(":")[3:]][0]
        vmlu = {"type": constants.DEVICE_VMLU,
                "devices": bdf, "stub": True,
                "name": "_".join((CAMBRICON_VMLU_DEV_PREFIX, bdf))}
        d_info = vmlu_device(path)
        vmlu.update(d_info)
        vmlu["stub"] = False
        traits = get_traits(vmlu["product_id"], fun_id, vf)
        vmlu.update(traits)
        vmlu["rc"] = constants.RESOURCES["VMLU"]
        return vmlu

    devs = []
    pf_has_vf = all_pfs_have_vf()
    for pf in all_pf_vmlus():
        vmlu = gen_vmlu_infos(pf, False)
        if pf in pf_has_vf:
            vmlu["mlu"] = []
            # All VFs here belong to one same physical MLU.
            vfs = all_vfs_in_pf_vmlus(pf)
            for vf in vfs:
                vf_vmlu = gen_vmlu_infos(vf, True)
                vmlu["mlu"].append(vf_vmlu)
        devs.append(_generate_driver_device(vmlu, pf in pf_has_vf))
    return devs


def _generate_driver_device(vmlu, pf_has_vf):
    driver_device_obj = driver_device.DriverDevice()
    driver_device_obj.vendor = vmlu["vendor"]
    driver_device_obj.stub = vmlu["stub"]
    driver_device_obj.model = vmlu.get('model', "miss_model_info")
    driver_device_obj.vendor_board_info = vmlu.get('vendor_board_info',
                                                   "miss_vb_info")
    std_board_info = {'product_id': vmlu.get('product_id', None)}
    driver_device_obj.std_board_info = jsonutils.dumps(std_board_info)
    driver_device_obj.type = vmlu["type"]
    driver_device_obj.controlpath_id = _generate_controlpath_id(vmlu)
    driver_device_obj.deployable_list = _generate_dep_list(vmlu, pf_has_vf)
    return driver_device_obj


def _generate_controlpath_id(vmlu):
    driver_cpid = driver_controlpath_id.DriverControlPathID()
    driver_cpid.cpid_type = "PCI"
    driver_cpid.cpid_info = utils.pci_str_to_json(vmlu["devices"])
    return driver_cpid


def _generate_dep_list(vmlu, pf_has_vf):
    driver_dep = driver_deployable.DriverDeployable()
    driver_dep.attribute_list = _generate_attribute_list(vmlu)
    driver_dep.attach_handle_list = []
    # pf without sriov enabled.
    if not pf_has_vf:
        driver_dep.num_accelerators = 1
        driver_dep.attach_handle_list = \
            [_generate_attach_handle(vmlu)]
        driver_dep.name = vmlu["name"]
        driver_dep.driver_name = DRIVER_NAME

    else:
        driver_dep.num_accelerators = len(vmlu["mlu"])
        for vf in vmlu["mlu"]:
            # Only vfs in mlu can be attach, no pf.
            driver_dep.attach_handle_list.append(
                _generate_attach_handle(vf))
            driver_dep.name = vf["name"]
            driver_dep.driver_name = DRIVER_NAME
    return [driver_dep]


def _generate_attach_handle(vmlu):
    driver_ah = driver_attach_handle.DriverAttachHandle()
    driver_ah.attach_type = constants.AH_TYPE_PCI
    driver_ah.attach_info = utils.pci_str_to_json(vmlu["devices"])
    driver_ah.in_use = False
    return driver_ah


def _generate_attribute_list(vmlu):
    attr_list = []
    index = 0
    for k, v in vmlu.items():
        if k == "rc":
            driver_attr = driver_attribute.DriverAttribute()
            driver_attr.key, driver_attr.value = k, v
            attr_list.append(driver_attr)
        if k == "traits":
            values = vmlu.get(k, None)
            for val in values:
                driver_attr = driver_attribute.DriverAttribute()
                driver_attr.key = "trait" + str(index)
                index = index + 1
                driver_attr.value = val
                attr_list.append(driver_attr)
    if vmlu.get("mlu"):
        for vf in vmlu["mlu"]:
            for k, values in vf.items():
                if k == "traits":
                    for val in values:
                        driver_attr = driver_attribute.DriverAttribute(
                            key="trait" + str(index), value=val)
                        index = index + 1
                        attr_list.append(driver_attr)
    return attr_list

