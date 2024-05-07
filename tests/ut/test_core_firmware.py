from unittest import mock

import munch
from cterasdk.core import firmwares
from tests.ut import base_core


class TestCoreFirmwares(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._mock_session = self.patch_call("cterasdk.objects.services.Management.session")

    def test_list_images_in_tenant_context(self):
        base_core.BaseCoreTest._enable_tenant_context(self._mock_session)
        execute_response = 'Success'
        self._init_global_admin(execute_response=execute_response)
        ret = firmwares.Firmwares(self._global_admin).list_images()
        self._global_admin.api.execute.assert_called_once_with('', 'getFirmwares', mock.ANY)
        expected_param = munch.Munch({'_classname': 'FirmwareParam'})
        actual_param = self._global_admin.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, execute_response)

    def test_list_images_global_admin(self):
        base_core.BaseCoreTest._disable_tenant_context(self._mock_session)
        get_response = 'Success'
        self._init_global_admin(get_response=get_response)
        ret = firmwares.Firmwares(self._global_admin).list_images()
        self._global_admin.api.get.assert_called_once_with('/firmwares')
        self.assertEqual(ret, get_response)