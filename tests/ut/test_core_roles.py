from unittest import mock
import munch

from cterasdk.core import roles
from cterasdk.core.enum import Role
from tests.ut import base_core


class TestCoreRoles(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._role = 'ReadWriteAdmin'

    def test_types(self):
        self._init_global_admin()
        ret = roles.Roles(self._global_admin).types()
        options = [v for k, v in Role.__dict__.items() if not k.startswith('_')]
        self._assert_equal_objects(ret, options)

    def test_get_role_not_found(self):
        self._init_global_admin()
        roles.Roles(self._global_admin).get('not_found')

    def test_get_role_success(self):
        self._init_global_admin(get_response=TestCoreRoles._role_settings(self._role))
        ret = roles.Roles(self._global_admin).get(self._role)
        self._global_admin.get.assert_called_once_with(f'/rolesSettings/{self._role}')
        self._assert_equal_objects(ret, TestCoreRoles._role_settings())

    def test_modify_role_not_found(self):
        self._init_global_admin()
        roles.Roles(self._global_admin).modify('not_found', None)

    def test_modify_role_success(self):
        role_settings = TestCoreRoles._role_settings(self._role)
        self._init_global_admin(put_response=role_settings)
        ret = roles.Roles(self._global_admin).modify(self._role, role_settings)
        self._global_admin.get.assert_called_once_with(f'/rolesSettings/{self._role}', mock.ANY)
        actual_param = self._global_admin.put.call_args[0][1]
        self._assert_equal_objects(actual_param, role_settings)
        self._assert_equal_objects(ret.to_server_object(), role_settings)

    @staticmethod
    def _role_settings(name):
        return munch.Munch({
            'name': name,
            'superUser': False,
            'allowRemoteWipe': True,
            'allowSSO': True,
            'allowSeedingExport': True,
            'allowSeedingImport': True,
            'canAccessEndUserFolders': True,
            'canChangePortalSettings': True,
            'canChangeRoles': True,
            'canChangeUserEmail': True,
            'canChangeUserPassword': True,
            'canManageAllFolders': True,
            'canManagePlans': True,
            'canManageUsers': True,
            'canManageLogSettings': False
        })
    

