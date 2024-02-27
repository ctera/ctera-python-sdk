from unittest import mock
import munch

from cterasdk.core import licenses
from tests.ut import base_core


class TestCoreLicenses(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._license = 'ABCD'

    def test_get_all_licenses(self):
        get_response = 'Success'
        self._init_global_admin(get_response=get_response)
        ret = licenses.Licenses(self._global_admin).all()
        self._global_admin.api.get.assert_called_once_with('/portalLicenses')
        self.assertEqual(ret, get_response)

    def test_add_license(self):
        execute_response = 'Success'
        self._init_global_admin(execute_response=execute_response)
        licenses.Licenses(self._global_admin).add(self._license)
        self._global_admin.api.execute.assert_called_once_with('', 'addLicenses', mock.ANY)
        actual_param = self._global_admin.api.execute.call_args[0][2]
        self.assertEqual(actual_param.keys[0], self._license)

    def test_remove_license(self):
        get_response = [munch.Munch({'key': self._license})]
        put_response = 'Success'
        self._init_global_admin(get_response=get_response, put_response='Success')
        ret = licenses.Licenses(self._global_admin).remove(self._license)
        self._global_admin.api.get.assert_called_once_with('/portalLicenses')
        self._global_admin.api.put.assert_called_once_with('/portalLicenses', [])
        self.assertEqual(ret, put_response)
