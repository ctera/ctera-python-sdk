from unittest import mock
import munch

from cterasdk.core import storage_classes
from cterasdk import exceptions
from tests.ut.core.admin import base_admin


class TestCoreStorageClasses(base_admin.BaseCoreTest):

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

    def test_list_storage_classes_in_tenant_context(self):
        base_admin.BaseCoreTest.enable_tenant_context(self._mock_session)
        execute_response = 'Success'
        self._init_global_admin(execute_response=execute_response)
        ret = storage_classes.StorageClasses(self._global_admin).all()
        self._global_admin.api.execute.assert_called_once_with('', 'getStorageClasses')
        self.assertEqual(ret, execute_response)

    def test_list_storage_classes_global_admin(self):
        base_admin.BaseCoreTest.disable_tenant_context(self._mock_session)
        get_response = 'Success'
        self._init_global_admin(get_response=get_response)
        ret = storage_classes.StorageClasses(self._global_admin).all()
        self._global_admin.api.get.assert_called_once_with('/storageClasses')
        self.assertEqual(ret, get_response)

    def test_get_storage_class_global_admin(self):
        base_admin.BaseCoreTest.disable_tenant_context(self._mock_session)
        get_response = 'Success'
        self._init_global_admin(get_response=get_response)
        ret = storage_classes.StorageClasses(self._global_admin).get(self._storage_class_name)
        self._global_admin.api.get.assert_called_once_with(f'/storageClasses/{self._storage_class_name}')
        self.assertEqual(ret, get_response)

    def test_get_storage_class_in_tenant_context(self):
        base_admin.BaseCoreTest.enable_tenant_context(self._mock_session)
        execute_response = [munch.Munch({'name': self._storage_class_name})]
        self._init_global_admin(execute_response=execute_response)
        ret = storage_classes.StorageClasses(self._global_admin).get(self._storage_class_name)
        self._global_admin.api.execute.assert_called_once_with('', 'getStorageClasses')
        self.assertEqual(ret.name, self._storage_class_name)

    def test_get_storage_class_in_tenant_context_not_found(self):
        base_admin.BaseCoreTest.enable_tenant_context(self._mock_session)
        execute_response = []
        self._init_global_admin(execute_response=execute_response)
        with self.assertRaises(exceptions.CTERAException) as error:
            storage_classes.StorageClasses(self._global_admin).get(self._storage_class_name)
            self._global_admin.api.execute.assert_called_once_with('', 'getStorageClasses')
        self.assertEqual('Could not find storage class.', error.exception.message)
