from unittest import mock
import munch

from cterasdk.core import storage_classes
from tests.ut import base_core


class TestCoreStorageClasses(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._storage_class_name = 'Test'
        self._mock_session = self.patch_call("cterasdk.objects.services.Management.session")

    def test_add_storage_class(self):
        add_response = 'Success'
        self._init_global_admin(add_response=add_response)
        ret = storage_classes.StorageClasses(self._global_admin).add(self._storage_class_name)
        self._global_admin.api.add.assert_called_once_with('/storageClasses', mock.ANY)
        actual_param = self._global_admin.api.add.call_args[0][1]
        expected_param = munch.Munch(dict(name=self._storage_class_name))
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, add_response)

    def test_get_storage_class_global_admin(self):
        self._mock_session.in_tenant_context = mock.MagicMock()
        self._mock_session.in_tenant_context.return_value = True
        get_response = 'Success'
        self._init_global_admin(get_response=get_response)
        ret = storage_classes.StorageClasses(self._global_admin).get(self._storage_class_name)
        self._global_admin.api.get.assert_called_once_with(f'/storageClasses/{self._storage_class_name}')
        self.assertEqual(ret, get_response)