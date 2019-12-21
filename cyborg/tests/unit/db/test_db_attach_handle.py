# Copyright 2020 ZTE Corporation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Tests for manipulating AttachHandle via the DB API"""

from oslo_utils import uuidutils

from cyborg.common import exception
from cyborg.tests.unit.db import base


class TestDbAttachHandleTestCase(base.DbTestCase):

    def test_get_by_uuid_not_exist(self):
        random_uuid = uuidutils.generate_uuid()
        self.assertRaises(exception.ResourceNotFound,
                          self.dbapi.attach_handle_get_by_uuid,
                          self.context, random_uuid)

    def test_delete_by_uuid_not_exist(self):
        random_uuid = uuidutils.generate_uuid()
        self.assertRaises(exception.ResourceNotFound,
                          self.dbapi.attach_handle_delete,
                          self.context, random_uuid)

    def test_do_allocate_attach_handle(self):
        dep_id = 100
        self.assertRaises(exception.ResourceNotFound,
                          self.dbapi._do_allocate_attach_handle,
                          self.context, dep_id)
