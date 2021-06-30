from cterasdk.core import settings
from tests.ut import base_core


class TestCoreSettings(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._timezone = 'timezone'

    def test_get_timezone(self):
        self._init_global_admin(get_response=self._timezone)
        timezone = settings.Settings(self._global_admin).global_settings.get_timezone()
        self._global_admin.get.assert_called_once_with('/settings/timezone')
        self.assertEqual(timezone, self._timezone)

    def test_set_timezone(self):
        put_response = 'Success'
        self._init_global_admin(put_response=put_response)
        ret = settings.Settings(self._global_admin).global_settings.set_timezone(self._timezone)
        self._global_admin.put.assert_called_once_with('/settings/timezone', self._timezone)
        self.assertEqual(ret, put_response)
