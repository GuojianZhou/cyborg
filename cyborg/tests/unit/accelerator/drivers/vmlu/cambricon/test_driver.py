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


import fixtures
import mock
import os

from cyborg.accelerator.drivers.vmlu.cambricon.driver import cambriconVMLUDriver
from cyborg.accelerator.drivers.vmlu.cambricon import sysinfo
from cyborg.tests import base
from cyborg.tests.unit.accelerator.drivers.vmlu.cambricon import prepare_test_data

class TestcambriconVMLUDriver(base.TestCase):

    def setUp(self):
        super(TestcambriconVMLUDriver, self).setUp()
        self.syspath = sysinfo.SYS_VMLU
        self.pcipath = sysinfo.PCI_DEVICES_PATH
        self.pcipath_pattern = sysinfo.PCI_DEVICES_PATH_PATTERN
        tmp_sys_dir = self.useFixture(fixtures.TempDir())
        prepare_test_data.create_fake_sysfs(tmp_sys_dir.path)
        tmp_path = tmp_sys_dir.path
        sysinfo.SYS_VMLU = os.path.join(
            tmp_path, sysinfo.SYS_VMLU.split("/", 1)[-1])
        sysinfo.PCI_DEVICES_PATH = os.path.join(
            tmp_path, sysinfo.PCI_DEVICES_PATH.split("/", 1)[-1])
        sysinfo.PCI_DEVICES_PATH_PATTERN = os.path.join(
            tmp_path, sysinfo.PCI_DEVICES_PATH_PATTERN.split("/", 1)[-1])

    def tearDown(self):
        super(TestcambriconVMLUDriver, self).tearDown()
        sysinfo.SYS_VMLU = self.syspath
        sysinfo.PCI_DEVICES_PATH = self.pcipath
        sysinfo.PCI_DEVICES_PATH_PATTERN = self.pcipath_pattern

    def test_discover(self):
        attach_handle_list = [
            [
                {'attach_type': 'PCI',
                 'attach_info': '{"bus": "3b", '
                                '"device": "00", '
                                '"domain": "0000", '
                                '"function": "1"}',
                 'in_use': False}
            ],
            [
                {'attach_type': 'PCI',
                 'attach_info': '{"bus": "86", '
                                '"device": "00", '
                                '"domain": "0000", '
                                '"function": "0"}',
                 'in_use': False}
            ],
            [
                {'attach_type': 'PCI',
                 'attach_info': '{"bus": "af", '
                                '"device": "00", '
                                '"domain": "0000", '
                                '"function": "0"}',
                 'in_use': False}
            ]
        ]
        expected = [{'vendor': '0xcabc',
                     'type': 'VMLU',
                     'model': '0x0270',
                     'deployable_list':
                         [
                             {'num_accelerators': 1,
                              'name': 'cambricon-vmlu-dev_0000:3b:00.1',
                              'attach_handle_list': attach_handle_list[0]
                              },
                         ],
                     'controlpath_id':
                         {
                             'cpid_info': '{"bus": "3b", '
                                          '"device": "00", '
                                          '"domain": "0000", '
                                          '"function": "0"}',
                             'cpid_type': 'PCI'}
                     },
                    {'vendor': '0xcabc',
                     'type': 'VMLU',
                     'model': '0x0270',
                     'deployable_list':
                         [
                             {'num_accelerators': 1,
                              'name': 'cambricon-vmlu-dev_0000:86:00.0',
                              'attach_handle_list': attach_handle_list[1]
                              },
                         ],
                     'controlpath_id':
                         {
                             'cpid_info': '{"bus": "86", '
                                          '"device": "00", '
                                          '"domain": "0000", '
                                          '"function": "0"}',
                             'cpid_type': 'PCI'}
                     },
                    {'vendor': '0xcabc',
                     'type': 'VMLU',
                     'model': '0x0270',
                     'deployable_list':
                         [
                             {'num_accelerators': 1,
                              'name': 'cambricon-vmlu-dev_0000:af:00.0',
                              'attach_handle_list': attach_handle_list[2]
                              },
                         ],
                     'controlpath_id':
                         {
                             'cpid_info': '{"bus": "af", '
                                          '"device": "00", '
                                          '"domain": "0000", '
                                          '"function": "0"}',
                             'cpid_type': 'PCI'}
                     }
                    ]
        cambricon = cambriconVMLUDriver()
        vmlus = cambricon.discover()
        list.sort(vmlus, key=lambda x: x._obj_deployable_list[0].name)
        self.assertEqual(3, len(vmlus))
        for i in range(len(vmlus)):
            vmlu_dict = vmlus[i].as_dict()
            vmlu_dep_list = vmlu_dict['deployable_list']
            vmlu_attach_handle_list = \
                vmlu_dep_list[0].as_dict()['attach_handle_list']
            self.assertEqual(expected[i]['vendor'], vmlu_dict['vendor'])
            self.assertEqual(expected[i]['controlpath_id'],
                             vmlu_dict['controlpath_id'])
            self.assertEqual(expected[i]['deployable_list'][0]
                             ['num_accelerators'],
                             vmlu_dep_list[0].as_dict()['num_accelerators'])
            self.assertEqual(attach_handle_list[i][0],
                             vmlu_attach_handle_list[0].as_dict())
