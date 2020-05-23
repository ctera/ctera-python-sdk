from unittest import mock
import uuid
import munch

from cterasdk import exception
from cterasdk.common import Object
from cterasdk.core.types import UserAccount
from cterasdk.core import enum, query, union
from cterasdk.core import devices
from tests.ut import base_core


class TestCoreDevices(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._expected_code = str(uuid.uuid4())
        self._init_global_admin(get_response=munch.Munch(dict(code=self._expected_code)))
        self._username = 'admin'
        self._portal = 'portal'
        self._remote_command_mock = self.patch_call("cterasdk.core.devices.remote.remote_command")
        self._user_account = UserAccount('user')
        self._user_uid = 1337
        self._get_user_mock = self.patch_call("cterasdk.core.users.Users.get")

    def test_device_ok(self):
        o = Object()
        o.name = "unit-test"
        self._init_global_admin(get_multi_response=o)
        devices.Devices(self._global_admin).device(o.name)
        self._global_admin.get_multi.assert_called_once_with('/portals/None/devices/unit-test', mock.ANY)
        expected_include = ['/' + attr for attr in devices.Devices.default]
        actual_include = self._global_admin.get_multi.call_args[0][1]
        self.assertEqual(len(expected_include), len(actual_include))
        for attr in expected_include:
            self.assertIn(attr, actual_include)
        self._remote_command_mock.assert_called_once_with(self._global_admin, o)

    def test_device_notfound(self):
        o = Object()
        o.name = None
        self._init_global_admin(get_multi_response=o)
        with self.assertRaises(exception.CTERAException) as error:
            devices.Devices(self._global_admin).device(o.name)
        self.assertEqual('Device not found', error.exception.message)

    def test_filers_no_device_types(self):
        self._test_filers(None, enum.DeviceType.Gateways)

    def test_filers_with_device_types(self):
        device_types = [enum.DeviceType.vGateway, enum.DeviceType.C800]
        self._test_filers(device_types, device_types)

    def test_filers_with_mismatching_device_types(self):
        device_types = [enum.DeviceType.ServerAgent]
        self._test_filers(device_types, enum.DeviceType.Gateways)

    def _test_filers(self, device_types, expected_device_types_filters):
        devs = devices.Devices(self._global_admin)
        devs.devices = mock.MagicMock()
        devs.filers(deviceTypes=device_types)
        devs.devices.assert_called_once_with(None, False, mock.ANY)
        expected_filters = [query.FilterBuilder(devices.Devices.type_attr).eq(deviceType) for deviceType in expected_device_types_filters]
        self._verify_filters_list(expected_filters, devs.devices.call_args[0][2])

    def test_agents(self):
        devs = devices.Devices(self._global_admin)
        devs.devices = mock.MagicMock()
        devs.agents()
        devs.devices.assert_called_once_with(None, False, mock.ANY)
        expected_filters = [query.FilterBuilder(devices.Devices.type_attr).like('Agent')]
        self._verify_filters_list(expected_filters, devs.devices.call_args[0][2])

    def test_desktops(self):
        devs = devices.Devices(self._global_admin)
        devs.devices = mock.MagicMock()
        devs.desktops()
        devs.devices.assert_called_once_with(None, False, mock.ANY)
        expected_filters = [query.FilterBuilder(devices.Devices.type_attr).eq(enum.DeviceType.WorkstationAgent)]
        self._verify_filters_list(expected_filters, devs.devices.call_args[0][2])

    def test_servers(self):
        devs = devices.Devices(self._global_admin)
        devs.devices = mock.MagicMock()
        devs.servers()
        devs.devices.assert_called_once_with(None, False, mock.ANY)
        expected_filters = [query.FilterBuilder(devices.Devices.type_attr).eq(enum.DeviceType.ServerAgent)]
        self._verify_filters_list(expected_filters, devs.devices.call_args[0][2])

    def test_by_name(self):
        devs = devices.Devices(self._global_admin)
        devs.devices = mock.MagicMock()
        names = ['dev1', 'dev2']
        devs.by_name(names)
        devs.devices.assert_called_once_with(None, False, mock.ANY)
        expected_filters = [query.FilterBuilder('name').eq(name) for name in names]
        self._verify_filters_list(expected_filters, devs.devices.call_args[0][2])

    def _verify_filters_list(self, expected_filters, actual_filters):
        self.assertEqual(len(expected_filters), len(actual_filters))
        for expected_filter in expected_filters:
            match = False
            for actual_filter in actual_filters:
                if actual_filter.__dict__ == expected_filter.__dict__:
                    match = True
            self.assertEqual(match, True)

    def test_devices(self):
        self._test_devices()

    def test_devices_with_filters(self):
        self._test_devices([query.FilterBuilder('name').eq('test')])

    def test_devices_owned_by_user(self):
        self._mock_get_user()
        self._test_devices(user=self._user_account)

    def _test_devices(self, filters=None, user=None):
        with mock.patch("cterasdk.core.devices.query.iterator") as query_iterator_mock:
            o = Object()
            o.name = "unit-test"
            query_iterator_mock.return_value = [o]
            list(devices.Devices(self._global_admin).devices(filters=filters, user=user))
            if user:
                self._get_user_mock.assert_called_once_with(self._user_account, ['uid'])
            query_iterator_mock.assert_called_once_with(self._global_admin, '/devices', mock.ANY)
            expected_param = TestCoreDevices._get_expected_devices_params(filters=filters, user_uid=(self._user_uid if user else None))
            actual_param = query_iterator_mock.call_args[0][2]
            self._assert_equal_objects(actual_param, expected_param)
            self._remote_command_mock.assert_called_once_with(self._global_admin, o)

    @staticmethod
    def _get_expected_devices_params(include=None, all_portals=False, filters=None, user_uid=None):
        include = union.union(include or [], devices.Devices.default)
        builder = query.QueryParamBuilder().include(include).allPortals(all_portals)
        filters = filters or []
        for query_filter in filters:
            builder.addFilter(query_filter)
        builder.orFilter((len(filters) > 1))
        if user_uid:
            builder.ownedBy(user_uid)
        return builder.build()

    def _mock_get_user(self):
        param = Object()
        param.uid = self._user_uid
        self._get_user_mock.return_value = param
