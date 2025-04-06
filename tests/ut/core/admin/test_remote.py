from unittest import mock
import munch

from cterasdk.core import devices
from cterasdk.common import Object
from cterasdk.objects import Edge, Drive
from tests.ut.core.admin import base_admin


class TestCoreRemote(base_admin.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._device_name = 'device-name'
        self._tenant_name = 'team-portal-name'
        self._device_portal = f'objs/21//TeamPortal/{self._tenant_name}'

        self._device_remote_access_url = "http://corp.gfs.ctera.me/devices/device-name"

        self._user_name = 'user'
        self._user_role = 'EndUser'

        self._sso_ticket = 'sso ticket'

    def test_instantiation_of_remote_devices(self):
        filer_types = ['CloudPlug', 'C200', 'C400', 'C800', 'C800P', 'vGateway']
        agent_types = ['Server Agent', 'Workstation Agent']
        other_types = ['Mobile', 'Unknown']
        for filer_type in filer_types:
            get_multi_response = TestCoreRemote._create_device_param(self._device_name, self._device_portal,
                                                                     filer_type, self._device_remote_access_url)
            self._call_and_assert_instance_type(get_multi_response, Edge)
        for agent_type in agent_types:
            get_multi_response = TestCoreRemote._create_device_param(self._device_name, self._device_portal,
                                                                     agent_type, self._device_remote_access_url)
            self._call_and_assert_instance_type(get_multi_response, Drive)
        for other_type in other_types:
            get_multi_response = TestCoreRemote._create_device_param(self._device_name, self._device_portal,
                                                                     other_type, self._device_remote_access_url)
            self._call_and_assert_instance_type(get_multi_response, Object)

    def test_filer_remote_access(self):
        self.patch_call("cterasdk.lib.session.base.BaseSession.start_session")
        remote_session = self.patch_call("cterasdk.lib.session.edge.Session.start_remote_session")
        self.patch_call("cterasdk.edge.ctera_migrate.CTERAMigrate.login")
        remote_session.return_value = munch.Munch({'account': munch.Munch({'name': 'mickey', 'tenant': 'tenant'})})
        get_multi_response = TestCoreRemote._create_device_param(self._device_name, self._device_portal,
                                                                 'vGateway', self._device_remote_access_url)
        self._init_global_admin(get_multi_response=get_multi_response, execute_response=self._sso_ticket)
        self._activate_portal_session()
        portal_device = devices.Devices(self._global_admin).device(self._device_name)
        portal_device.get = mock.MagicMock()
        portal_device.remote_access()
        self._global_admin.api.execute.assert_called_once_with(f'/portals/{self._tenant_name}/devices/{self._device_name}',
                                                               'singleSignOn')
        # portal_device.get.assert_called_once_with('/ssologin', {'ticket': self._sso_ticket})

    def _call_and_assert_instance_type(self, get_multi_response, instance_type):
        self._init_global_admin(get_multi_response=get_multi_response)
        self._activate_portal_session()
        portal_device = devices.Devices(self._global_admin).device(self._device_name)
        self.assertIsInstance(portal_device, instance_type)

    def _activate_portal_session(self):
        self._global_admin.api.get = mock.MagicMock(side_effect=[TestCoreRemote._create_current_session_object(),
                                                                 'team-portal-name', '7.5.182.16'])
        self._global_admin.session().start_session(self._global_admin)

    @staticmethod
    def _create_device_param(name, portal, device_type, remote_access_url):
        param = Object()
        param.name = name
        param.portal = portal
        param.deviceType = device_type
        param.remoteAccessUrl = remote_access_url
        return param

    @staticmethod
    def _create_current_session_object():
        session = Object()
        session.username = 'admin'
        session.role = 'admin'
        session.domain = None
        return session
