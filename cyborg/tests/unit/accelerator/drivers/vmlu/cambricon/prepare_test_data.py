#!/usr/bin/python
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

import argparse
import copy
import glob
import os
import shutil


PF0_ADDR = "0000:3b:00.0"
PF1_ADDR = "0000:86:00.0"
PF2_ADDR = "0000:af:00.0"
VF0_ADDR = "0000:3b:00.1"
VF1_ADDR = "0000:3b:00.2"
VF2_ADDR = "0000:3b:00.3"
VF3_ADDR = "0000:3b:00.4"
VMLU_TREE = {
    "dev.0": {"bdf": PF0_ADDR,
              "mlu": {"dev.2": {"bdf": VF0_ADDR}, "dev.3": {"bdf": VF1_ADDR}}},
    "dev.1": {"bdf": PF1_ADDR},
    "dev.4": {"bdf": PF2_ADDR}}

SYS_DEVICES = "sys/devices"
PCI_DEVICES_PATH = "sys/bus/pci/devices"
SYS_CLASS_VMLU = "sys/class/vmlu"

DEV_PREFIX = "cambricon_dev"

PGFA_DEVICE_COMMON_SUB_DIR = ["power"]

PGFA_DEVICE_COMMON_CONTENT = {
    "broken_parity_status": "0",
    "class": "0x120000",
    "config": "",
    "consistent_dma_mask_bits": "64",
    "d3cold_allowed": "1",
    "device": "0x0270",
    "dma_mask_bits": "64",
    "driver_override": "(null)",
    "enable": "1",
    "irq": "16",
    "local_cpulist": "0-31",
    "local_cpus": "00000000,00000000,00000000,00000000,00000000,"
                  "00000000,00000000,00000000,00000000,00000000,"
                  "00000000,00000000,00000000,ffffffff",
    "modalias": "pci:v00008086d0000BCC0sv00000000sd00000000bc12sc00i00",
    "msi_bus": "",
    "numa_node": "-1",
    "resource": [
        "0x000038bfc0000000 0x000038bfcfffffff 0x000000000014220c",
        "0x0000000000000000 0x0000000000000000 0x0000000000000000",
        "0x000038bff4000000 0x000038bff7ffffff 0x000000000014220c",
        "0x0000000000000000 0x0000000000000000 0x0000000000000000",
        "0x000038bff0000000 0x000038bff3ffffff 0x000000000014220c",
        "0x0000000000000000 0x0000000000000000 0x0000000000000000",
        "0x0000000000000000 0x0000000000000000 0x0000000000000000",
        "0x000038bf80000000 0x000038bfbfffffff 0x000000000014220c",
        "0x0000000000000000 0x0000000000000000 0x0000000000000000",
        "0x000038bfe0000000 0x000038bfefffffff 0x000000000014220c",
        "0x0000000000000000 0x0000000000000000 0x0000000000000000",
        "0x000038bfd0000000 0x000038bfdfffffff 0x000000000014220c",
        "0x0000000000000000 0x0000000000000000 0x0000000000000000"],
    "resource0": "",
    "resource0_wc": "",
    "subsystem_device": "0x0000",
    "subsystem_vendor": "0x0000",
    "uevent": [
        "DRIVER=cambricon-pci-drv",
        "PCI_CLASS=120000",
        "PCI_ID=cabc:0270",
        "PCI_SUBSYS_ID=0000:0000",
        "PCI_SLOT_NAME=0000:3b:00.0",
        "MODALIAS=pci:v0000CABCd00000270sv0000CABCsd00000012bc12sc00i00"],
    "vendor": "0xcabc"}

PGFA_DEVICES_SPECIAL_COMMON_CONTENT = {
    "dev.0": {
        "device": "0x0270",
        "modalias": "pci:v0000CABCd00000270sv0000CABCsd00000012bc12sc00i00",
        "irq": "0",
        "resource": [
            "0x000038bfc0000000 0x000038bfcfffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x000038bff4000000 0x000038bff7ffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x000038bff0000000 0x000038bff3ffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x000038bf80000000 0x000038bfbfffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x000038bfe0000000 0x000038bfefffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x000038bfd0000000 0x000038bfdfffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000"],
        "resource2": "",
        "resource2_wc": "",
        "sriov_numvfs": "4",
        "sriov_totalvfs": "4",
        "uevent": [
            "DRIVER=cambricon-pci-drv",
            "PCI_CLASS=120000",
            "PCI_ID=CABC:0270",
            "PCI_SUBSYS_ID=CABC:0012",
            "PCI_SLOT_NAME=0000:3b:00.0",
            "MODALIAS=pci:v0000CABCd00000270sv0000CABCsd00000012bc12sc00i00"],
    },
    "dev.1": {
        "device": "0x0270",
        "modalias": "pci:v0000CABCd00000270sv0000CABCsd00000012bc12sc00i00",
        "irq": "0",
        "resource": [
            "0x000038bfc0000000 0x000038bfcfffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x000038bff4000000 0x000038bff7ffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x000038bff0000000 0x000038bff3ffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x000038bf80000000 0x000038bfbfffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x000038bfe0000000 0x000038bfefffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x000038bfd0000000 0x000038bfdfffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000"],
        "resource2": "",
        "resource2_wc": "",
        "sriov_numvfs": "0",
        "sriov_totalvfs": "4",
        "uevent": [
            "DRIVER=cambricon-pci-drv",
            "PCI_CLASS=120000",
            "PCI_ID=CABC:0270",
            "PCI_SUBSYS_ID=CABC:0012",
            "PCI_SLOT_NAME=0000:86:00.0",
            "MODALIAS=pci:v0000CABCd00000270sv0000CABCsd00000012bc12sc00i00"],
    },
    "dev.2": {
        "device": "0x0271",
        "modalias": "pci:v0000CABCd00000271sv0000CABCsd00000012bc12sc00i00",
        "irq": "0",
        "resource": [
            "0x000038bf80000000 0x000038bf8fffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x000038bfe0000000 0x000038bfe3ffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x000038bfd0000000 0x000038bfd3ffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000"],
        "uevent": [
            "DRIVER=cambricon-pci-drv",
            "PCI_CLASS=120000",
            "PCI_ID=CABC:0271",
            "PCI_SUBSYS_ID=CABC:0012",
            "PCI_SLOT_NAME=0000:3b:00.1",
            "MODALIAS=pci:v0000CABCd00000271sv0000CABCsd00000012bc12sc00i00"],
    },
    "dev.3": {
        "device": "0x0271",
        "modalias": "pci:v0000CABCd00000271sv0000CABCsd00000012bc12sc00i00",
        "irq": "0",
        "resource": [
            "0x000038bf80000000 0x000038bf8fffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x000038bfe0000000 0x000038bfe3ffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x000038bfd0000000 0x000038bfd3ffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000"],
        "uevent": [
            "DRIVER=cambricon-pci-drv",
            "PCI_CLASS=120000",
            "PCI_ID=CABC:0271",
            "PCI_SUBSYS_ID=CABC:0012",
            "PCI_SLOT_NAME=0000:3b:00.2",
            "MODALIAS=pci:v0000CABCd00000271sv0000CABCsd00000012bc12sc00i00"],
    },
    "dev.4": {
        "device": "0x0270",
        "modalias": "pci:v0000CABCd00000270sv0000CABCsd00000012bc12sc00i00",
        "irq": "0",
        "resource": [
            "0x000039bfc0000000 0x000039bfcfffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x000039bff4000000 0x000039bff7ffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x000039bff0000000 0x000039bff3ffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x000039bf80000000 0x000039bfbfffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x000039bfe0000000 0x000039bfefffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000",
            "0x000039bfd0000000 0x000039bfdfffffff 0x000000000014220c",
            "0x0000000000000000 0x0000000000000000 0x0000000000000000"],
        "resource2": "",
        "resource2_wc": "",
        "sriov_numvfs": "0",
        "sriov_totalvfs": "4",
        "uevent": [
            "DRIVER=cambricon-pci-drv",
            "PCI_CLASS=120000",
            "PCI_ID=CABC:0270",
            "PCI_SUBSYS_ID=CABC:0012",
            "PCI_SLOT_NAME=0000:af:00.0",
            "MODALIAS=pci:v0000CABCd00000270sv0000CABCsd00000012bc12sc00i00"],
    }
}

PGFA_DEVICE_COMMON_SOFT_LINK = {
    "driver": "../../../bus/pci/drivers/cambricon-pci-drv",
    "iommu": "../../virtual/iommu/dmar8",
    "iommu_group": "../../../kernel/iommu_groups/75",
    "subsystem": "../../../bus/pci"
}

PGFA_DEVICES_SPECIAL_SOFT_LINK = {
    "dev.0": {
        "iommu": "../../virtual/iommu/dmar5",
        "iommu_group": "../../../kernel/iommu_groups/36",
    },
    "dev.1": {
        "iommu": "../../virtual/iommu/dmar1",
        "iommu_group": "../../../kernel/iommu_groups/58",
    },
    "dev.2": {
        "iommu": "../../virtual/iommu/dmar5",
        "iommu_group": "../../../kernel/iommu_groups/79",
    },
    "dev.3": {
        "iommu": "../../virtual/iommu/dmar5",
        "iommu_group": "../../../kernel/iommu_groups/80",
    },
    "dev.4": {
        "iommu": "../../virtual/iommu/dmar2",
        "iommu_group": "../../../kernel/iommu_groups/67",
    }
}

PGFA_DEVICE_PF_SOFT_LINK = {
    "virtfn": lambda k, v: (k + str(int(v.rsplit(".", 1)[-1]) - 1),
                            "/".join(["..", v]))
}

PGFA_DEVICE_VF_SOFT_LINK = {
    "physfn": lambda k, v: (k, "/".join(["..", v]))
}


def gen_vmlu_content(path, dev):
    content = copy.copy(PGFA_DEVICE_COMMON_CONTENT)
    content.update(PGFA_DEVICES_SPECIAL_COMMON_CONTENT[dev])
    for k, v in content.items():
        p = os.path.join(path, k)
        if not v:
            os.mknod(p)
        elif type(v) is str:
            with open(p, 'a') as f:
                f.write(v + "\n")
        elif type(v) is list:
            with open(p, 'a') as f:
                f.writelines([item + "\n" for item in v])


def gen_vmlu_sub_dir(path):
    for d in PGFA_DEVICE_COMMON_SUB_DIR:
        p = os.path.join(path, d)
        os.makedirs(p)


def gen_vmlu_pf_soft_link(path, bdf):
    for k, v in PGFA_DEVICE_PF_SOFT_LINK.items():
        if callable(v):
            k, v = v(k, bdf)
        os.symlink(v, os.path.join(path, k))


def gen_vmlu_common_soft_link(path, bdf):
    for k, v in PGFA_DEVICE_COMMON_SOFT_LINK.items():
        os.symlink(v, os.path.join(path, k))


def gen_vmlu_vf_soft_link(path, bdf):
    for k, v in PGFA_DEVICE_VF_SOFT_LINK.items():
        if callable(v):
            k, v = v(k, bdf)
        os.symlink(v, os.path.join(path, k))


def create_devices_path_and_files(tree, device_path, class_vmlu_path,
                                  vf=False, pfinfo=None):
    for k, v in tree.items():
        bdf = v["bdf"]
        pci_path = "pci" + bdf.rsplit(":", 1)[0]
        bdf_path = os.path.join(device_path, pci_path, bdf)
        ln = "-".join([DEV_PREFIX, k])
        dev_path = os.path.join(bdf_path, "vmlu", ln)
        os.makedirs(dev_path)
        gen_vmlu_content(bdf_path, k)
        gen_vmlu_sub_dir(bdf_path)
        if vf:
            gen_vmlu_pf_soft_link(pfinfo["path"], bdf)
            gen_vmlu_vf_soft_link(bdf_path, pfinfo["bdf"])
        pfinfo = {"path": bdf_path, "bdf": bdf}
        if "mlu" in v:
            create_devices_path_and_files(
                v["mlu"], device_path, class_vmlu_path, True, pfinfo)
        source = dev_path.split("sys")[-1]
        os.symlink("../.." + source, os.path.join(class_vmlu_path, ln))
        os.symlink("../../../" + bdf, os.path.join(dev_path, "device"))
        pci_dev = os.path.join(device_path.split(SYS_DEVICES)[0],
                               PCI_DEVICES_PATH)
        if not os.path.exists(pci_dev):
            os.makedirs(pci_dev)
        os.symlink("../../.." + bdf_path.split("sys")[-1],
                   os.path.join(pci_dev, bdf))


def create_devices_soft_link(class_vmlu_path):
    devs = glob.glob1(class_vmlu_path, "*")
    for dev in devs:
        path = os.path.realpath("%s/%s/device" % (class_vmlu_path, dev))
        softlinks = copy.copy(PGFA_DEVICE_COMMON_SOFT_LINK)
        softlinks.update(
            PGFA_DEVICES_SPECIAL_SOFT_LINK[dev.rsplit("-", 1)[-1]])
        for k, v in softlinks.items():
            source = os.path.normpath(os.path.join(path, v))
            if not os.path.exists(source):
                os.makedirs(source)
            os.symlink(v, os.path.join(path, k))


def create_fake_sysfs(prefix=""):
    sys_device = os.path.join(prefix, SYS_DEVICES)
    sys_class_vmlu = os.path.join(prefix, SYS_CLASS_VMLU)
    basedir = os.path.dirname(sys_device)
    if os.path.exists(basedir):
        shutil.rmtree(basedir, ignore_errors=False, onerror=None)
    os.makedirs(sys_class_vmlu)
    create_devices_path_and_files(VMLU_TREE, sys_device, sys_class_vmlu)
    create_devices_soft_link(sys_class_vmlu)


def main():
    create_fake_sysfs()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a fake sysfs for cambricon VMLU.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-p", "--prefix", type=str,
                        default="/tmp", dest="p",
                        help='Set the prefix path of the fake sysfs. '
                        'default "/tmp"')
    args = parser.parse_args()

    create_fake_sysfs(args.p)
