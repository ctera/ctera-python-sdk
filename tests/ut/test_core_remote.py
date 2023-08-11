from unittest import mock

from cterasdk.core import devices
from cterasdk.common import Object
from cterasdk.object import Gateway, Agent
from tests.ut import base_core


class TestCoreRemote(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._device_name = 'device-name'
        self._device_portal = 'team-portal-name'

        self._user_name = 'user'
        self._user_role = 'EndUser'

        self._sso_ticket = 'sso ticket'

    def test_instantiation_of_remote_devices(self):
        filer_types = ['CloudPlug', 'C200', 'C400', 'C800', 'C800P', 'vGateway']
        agent_types = ['Server Agent', 'Workstation Agent']
        other_types = ['Mobile', 'Unknown']
        for filer_type in filer_types:
            get_multi_response = TestCoreRemote._create_device_param(self._device_name, self._device_portal, filer_type)
            self._call_and_assert_instance_type(get_multi_response, Gateway)
        for agent_type in agent_types:
            get_multi_response = TestCoreRemote._create_device_param(self._device_name, self._device_portal, agent_type)
            self._call_and_assert_instance_type(get_multi_response, Agent)
        for other_type in other_types:
            get_multi_response = TestCoreRemote._create_device_param(self._device_name, self._device_portal, other_type)
            self._call_and_assert_instance_type(get_multi_response, Object)

    def test_filer_remote_access(self):
        get_multi_response = TestCoreRemote._create_device_param(self._device_name, self._device_portal, 'vGateway')
        self._init_global_admin(get_multi_response=get_multi_response, execute_response=self._sso_ticket)
        self._activate_portal_session()
        portal_device = devices.Devices(self._global_admin).device(self._device_name)
        portal_device.get = mock.MagicMock()
        portal_device.remote_access()
        self._global_admin.execute.assert_called_once_with(f'/portals/{self._device_portal}/devices/{self._device_name}',
                                                           'singleSignOn')
        portal_device.get.assert_called_once_with('/ssologin', {'ticket': self._sso_ticket})

    def _call_and_assert_instance_type(self, get_multi_response, instance_type):
        self._init_global_admin(get_multi_response=get_multi_response)
        self._activate_portal_session()
        portal_device = devices.Devices(self._global_admin).device(self._device_name)
        self.assertIsInstance(portal_device, instance_type)

    def _activate_portal_session(self):
        self._global_admin.get = mock.MagicMock(side_effect=['team-portal-name', '7.5.182.16',
                                                TestCoreRemote._create_current_session_object()])
        self._global_admin.session().start_local_session(self._global_admin)

    @staticmethod
    def _create_device_param(name, portal, device_type):
        param = Object()
        param.name = name
        param.portal = portal
        param.deviceType = device_type
        return param

    @staticmethod
    def _create_current_session_object():
        session = Object()
        session.username = 'admin'
        session.role = 'admin'
        return session
