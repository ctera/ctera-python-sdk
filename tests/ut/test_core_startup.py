from unittest import mock

import munch
from cterasdk.core import startup
from cterasdk import exceptions
from tests.ut import base_core


class TestCoreStartup(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._timezone = 'timezone'
        self._mock_session = self.patch_call("cterasdk.objects.services.Management.session")

    def test_status_success(self):
        status = 'Success'
        get_response = munch.Munch({'status': status})
        self._init_global_admin(get_response=get_response)
        ret = startup.Startup(self._global_admin).get()
        self._global_admin.api.get.assert_called_once_with('/startup')
        self.assertEqual(ret, status)

    def test_wait_success(self):
        get_response = munch.Munch({'status': 'Started'})
        self._init_global_admin(get_response=get_response)
        startup.Startup(self._global_admin).wait()

    def test_wait_timed_out(self):
        self.patch_call('time.sleep')
        status = 'Random Status'
        get_response = munch.Munch({'status': status})
        self._init_global_admin(get_response=get_response)
        with self.assertRaises(exceptions.CTERAException) as error:
            startup.Startup(self._global_admin).wait(retries=2, seconds=1)
        self.assertEqual('Timed out. Server did not start in a timely manner', error.exception.message)