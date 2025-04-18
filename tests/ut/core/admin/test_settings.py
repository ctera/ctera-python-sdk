from unittest import mock

import munch
from cterasdk.core import settings
from tests.ut.core.admin import base_admin


class TestCoreSettings(base_admin.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._timezone = 'timezone'
        self._mock_session = self.patch_call("cterasdk.objects.services.Management.session")

    def test_get_timezone(self):
        self._init_global_admin(get_response=self._timezone)
        timezone = settings.Settings(self._global_admin).global_settings.get_timezone()
        self._global_admin.api.get.assert_called_once_with('/settings/timezone')
        self.assertEqual(timezone, self._timezone)

    def test_set_timezone(self):
        put_response = 'Success'
        self._init_global_admin(put_response=put_response)
        ret = settings.Settings(self._global_admin).global_settings.set_timezone(self._timezone)
        self._global_admin.api.put.assert_called_once_with('/settings/timezone', self._timezone)
        self.assertEqual(ret, put_response)

    def test_update_settings_in_tenant_context(self):
        portal_settings = 'Settings'
        self._init_global_admin()
        self.enable_tenant_context(self._mock_session)
        settings.Settings(self._global_admin).portal.update(portal_settings)
        self._global_admin.api.execute.assert_called_once_with('', 'setSettings', mock.ANY)
        expected_param = munch.Munch({'_classname': 'SettingsParam', 'fromSystem': False, 'settings': portal_settings})
        actual_param = self._global_admin.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

    def test_use_global_settings_in_tenant_context(self):
        self._init_global_admin()
        self.enable_tenant_context(self._mock_session)
        settings.Settings(self._global_admin).portal.use_global_settings()
        self._global_admin.api.execute.assert_called_once_with('', 'setSettings', mock.ANY)
        expected_param = munch.Munch({'_classname': 'SettingsParam', 'fromSystem': True})
        actual_param = self._global_admin.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

    def test_update_settings_global_admin(self):
        portal_settings = 'Settings'
        self._init_global_admin()
        self.disable_tenant_context(self._mock_session)
        settings.Settings(self._global_admin).portal.update(portal_settings)
        self._global_admin.api.put.assert_called_once_with('/settings/defaultPortalSettings', portal_settings)

    def test_get_settings_in_tenant_context(self):
        portal_settings = 'Success'
        execute_response = munch.Munch({'settings': portal_settings})
        self.enable_tenant_context(self._mock_session)
        self._init_global_admin(execute_response=execute_response)
        ret = settings.Settings(self._global_admin).portal.get()
        self._global_admin.api.execute.assert_called_once_with('', 'getSettings')
        self.assertEqual(ret, portal_settings)

    def test_get_settings_global_admin(self):
        get_response = 'Success'
        self.disable_tenant_context(self._mock_session)
        self._init_global_admin(get_response=get_response)
        ret = settings.Settings(self._global_admin).portal.get()
        self._global_admin.api.get.assert_called_once_with('/settings/defaultPortalSettings')
        self.assertEqual(ret, get_response)
