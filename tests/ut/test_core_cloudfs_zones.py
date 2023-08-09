# pylint: disable=protected-access
import re
from unittest import mock

from cterasdk import exception
from cterasdk.common import Object
from cterasdk.core.enum import PolicyType
from cterasdk.core.types import CloudFSFolderFindingHelper, UserAccount
from cterasdk.core import query
from cterasdk.core import cloudfs
from tests.ut import base_core


class TestCoreZones(base_core.BaseCoreTest):

    _zone_name = 'EndZone'
    _zone_info = 'Welcome to CTERA Zones'
    _zone_policy_type = PolicyType.SELECT
    _zone_id = 1000
    _cloud_folders = dict(
        alice=dict(
            docs=dict(uid=1000, owner='objs/24639/test/PortalUser/alice'),
            music=dict(uid=1001, owner='objs/24639/test/PortalUser/alice')
        ),
        bruce=dict(
            docs=dict(uid=1002, owner='objs/24655/test/PortalUser/bruce'),
        )
    )

    def setUp(self):
        super().setUp()
        self._find_folder_helpers = [
            CloudFSFolderFindingHelper('docs', UserAccount('alice')),
            CloudFSFolderFindingHelper('music', UserAccount('alice')),
            CloudFSFolderFindingHelper('docs', UserAccount('bruce'))
        ]
        self._zone_name = TestCoreZones._zone_name
        self._zone_id = TestCoreZones._zone_id
        self._device_names = ['dev1', 'dev2', 'dev3']
        self._device_ids = [100, 101, 102]

    def test_get_zone_success(self):
        execute_response = self._get_zones_display_info_response()
        self._init_global_admin(execute_response=execute_response)
        ret = cloudfs.Zones(self._global_admin).get(self._zone_name)
        self._global_admin.execute.assert_called_once_with('', 'getZonesDisplayInfo', mock.ANY)
        query_filter = base_core.BaseCoreTest._create_filter(query.FilterType.String, 'name', query.Restriction.EQUALS, self._zone_name)
        expected_param = base_core.BaseCoreTest._create_query_params(include_classname=True, start_from=0, count_limit=1,
                                                                     filters=[query_filter], or_filter=False)
        actual_param = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret.zoneId, self._zone_id)

    def test_get_zone_raise(self):
        execute_response = TestCoreZones._get_zones_display_info_empty_response()
        self._init_global_admin(execute_response=execute_response)

        with self.assertRaises(exception.CTERAException) as error:
            cloudfs.Zones(self._global_admin).get(self._zone_name)

        self._global_admin.execute.assert_called_once_with('', 'getZonesDisplayInfo', mock.ANY)
        query_filter = base_core.BaseCoreTest._create_filter(query.FilterType.String, 'name', query.Restriction.EQUALS, self._zone_name)
        expected_param = base_core.BaseCoreTest._create_query_params(include_classname=True, start_from=0, count_limit=1,
                                                                     filters=[query_filter], or_filter=False)
        actual_param = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual('Zone not found', error.exception.message)

    def test_add_zone_default_args_success(self):
        execute_response = TestCoreZones._get_add_zone_response('OK')
        self._init_global_admin(execute_response=execute_response)
        cloudfs.Zones(self._global_admin).add(self._zone_name)
        self._global_admin.execute.assert_called_once_with('', 'addZone', mock.ANY)
        expected_param = self._get_zone_param()
        actual_param = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

    def test_add_zone_raise(self):
        execute_response = TestCoreZones._get_add_zone_response('Expected Failure')
        self._init_global_admin(execute_response=execute_response)
        with self.assertRaises(exception.CTERAException) as error:
            cloudfs.Zones(self._global_admin).add(self._zone_name)
        self._global_admin.execute.assert_called_once_with('', 'addZone', mock.ANY)
        expected_param = self._get_zone_param()
        actual_param = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual('Zone creation failed', error.exception.message)

    def test_add_folders_success(self):
        self._init_global_admin()
        zone = self._get_zones_display_info_response().objects.pop()
        self._global_admin.execute = mock.MagicMock(side_effect=TestCoreZones._mock_execute)
        self._global_admin.cloudfs.zones.get = mock.MagicMock(return_value=zone)
        find_cloud_folder_mock = self.patch_call("cterasdk.core.zones.cloudfs.CloudFS.find")
        find_cloud_folder_mock.side_effect = mock.MagicMock(side_effect=TestCoreZones._find_cloud_folder)

        cloudfs.Zones(self._global_admin).add_folders(self._zone_name, self._find_folder_helpers)

        self._global_admin.cloudfs.zones.get.assert_called_once_with(self._zone_name)
        find_folder_calls = []
        for find_folder_helper in self._find_folder_helpers:
            find_folder_calls.append(mock.call(find_folder_helper.name, find_folder_helper.owner, include=['uid', 'owner']))
        find_cloud_folder_mock.assert_has_calls(find_folder_calls)
        self._global_admin.execute.assert_has_calls(
            [
                mock.call('', 'getZoneBasicInfo', self._zone_id),
                mock.call('', 'saveZone', mock.ANY)
            ]
        )
        expected_param = self._get_add_folders_param()
        actual_param = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

    def test_add_folders_raise(self):
        self._init_global_admin()
        zone = self._get_zones_display_info_response().objects.pop()
        self._global_admin.execute = mock.MagicMock(side_effect=TestCoreZones._save_zone_side_effect)
        self._global_admin.cloudfs.zones.get = mock.MagicMock(return_value=zone)
        find_cloud_folder_mock = self.patch_call("cterasdk.core.zones.cloudfs.CloudFS.find")
        find_cloud_folder_mock.side_effect = mock.MagicMock(side_effect=TestCoreZones._find_cloud_folder)

        with self.assertRaises(exception.CTERAException) as error:
            cloudfs.Zones(self._global_admin).add_folders(self._zone_name, self._find_folder_helpers)

        self._global_admin.cloudfs.zones.get.assert_called_once_with(self._zone_name)
        find_folder_calls = []
        for find_folder_helper in self._find_folder_helpers:
            find_folder_calls.append(mock.call(find_folder_helper.name, find_folder_helper.owner, include=['uid', 'owner']))
        find_cloud_folder_mock.assert_has_calls(find_folder_calls)
        self._global_admin.execute.assert_has_calls(
            [
                mock.call('', 'getZoneBasicInfo', self._zone_id),
                mock.call('', 'saveZone', mock.ANY)
            ]
        )
        expected_param = self._get_add_folders_param()
        actual_param = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual('Failed adding folders to zone', error.exception.message)

    def test_add_devices_success(self):
        self._init_global_admin()
        zone = self._get_zones_display_info_response().objects.pop()
        self._global_admin.execute = mock.MagicMock(side_effect=TestCoreZones._mock_execute)
        self._global_admin.cloudfs.zones.get = mock.MagicMock(return_value=zone)
        query_devices_mock = self.patch_call("cterasdk.core.zones.devices.Devices.by_name")
        query_devices_mock.return_value = self._get_device_objects()

        cloudfs.Zones(self._global_admin).add_devices(self._zone_name, self._device_names)

        self._global_admin.cloudfs.zones.get.assert_called_once_with(self._zone_name)
        query_devices_mock.assert_called_once_with(include=['uid'], names=self._device_names)
        self._global_admin.execute.assert_has_calls(
            [
                mock.call('', 'getZoneBasicInfo', self._zone_id),
                mock.call('', 'saveZone', mock.ANY)
            ]
        )
        expected_param = self._get_add_devices_param()
        actual_param = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

    def test_add_devices_raise(self):
        self._init_global_admin()
        zone = self._get_zones_display_info_response().objects.pop()
        self._global_admin.execute = mock.MagicMock(side_effect=TestCoreZones._save_zone_side_effect)
        self._global_admin.cloudfs.zones.get = mock.MagicMock(return_value=zone)
        query_devices_mock = self.patch_call("cterasdk.core.zones.devices.Devices.by_name")
        query_devices_mock.return_value = self._get_device_objects()

        with self.assertRaises(exception.CTERAException) as error:
            cloudfs.Zones(self._global_admin).add_devices(self._zone_name, self._device_names)

        self._global_admin.cloudfs.zones.get.assert_called_once_with(self._zone_name)
        query_devices_mock.assert_called_once_with(include=['uid'], names=self._device_names)
        self._global_admin.execute.assert_has_calls(
            [
                mock.call('', 'getZoneBasicInfo', self._zone_id),
                mock.call('', 'saveZone', mock.ANY)
            ]
        )
        expected_param = self._get_add_devices_param()
        actual_param = self._global_admin.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual('Failed adding devices to zone', error.exception.message)

    def _get_add_devices_param(self):
        param = self._get_zone_param(zone_id=self._zone_id)
        for device_id in self._device_ids:
            param.delta.devicesDelta.added.append(device_id)
        return param

    def _get_add_folders_param(self):
        param = self._get_zone_param(zone_id=self._zone_id)
        param.delta.policyDelta = []
        for cloud_folders in TestCoreZones._cloud_folders.values():
            owner_id = None
            folder_ids = []
            for folder_info in cloud_folders.values():
                owner_id = re.search("[1-9][0-9]*", folder_info['owner']).group(0)
                folder_ids.append(folder_info['uid'])
            policyDelta = Object()
            policyDelta._classname = 'ZonePolicyDelta'  # pylint: disable=protected-access
            policyDelta.userUid = owner_id
            policyDelta.foldersDelta = Object()
            policyDelta.foldersDelta._classname = 'ZoneFolderDelta'  # pylint: disable=protected-access
            policyDelta.foldersDelta.added = folder_ids
            policyDelta.foldersDelta.removed = []
            param.delta.policyDelta.append(policyDelta)
        return param

    def _get_device_objects(self):
        devices = []
        for device_id in self._device_ids:
            param = Object()
            param.uid = device_id
            devices.append(param)
        return devices

    @staticmethod
    def _find_cloud_folder(folder_name, folder_owner, include):
        # pylint: disable=unused-argument
        folder_info = TestCoreZones._cloud_folders[folder_owner.name][folder_name]
        param = Object()
        param.uid = folder_info['uid']
        param.owner = folder_info['owner']
        return param

    @staticmethod
    def _save_zone_side_effect(path, name, param):
        if name == 'saveZone':
            return TestCoreZones._get_add_zone_response('Expected Failure')
        return TestCoreZones._mock_execute(path, name, param)

    @staticmethod
    def _mock_execute(path, name, param):
        # pylint: disable=unused-argument
        param = Object()
        if name == 'getZoneBasicInfo':
            param.name = TestCoreZones._zone_name
            param.info = TestCoreZones._zone_info
            param.policyType = TestCoreZones._zone_policy_type
            param.zoneId = TestCoreZones._zone_id
        elif name == 'saveZone':
            param = TestCoreZones._get_add_zone_response('OK')
        return param

    def test_delete_zone_success(self):
        self._init_global_admin(execute_response='ok')
        zone = self._get_zones_display_info_response().objects.pop()
        self._global_admin.cloudfs.zones.get = mock.MagicMock(return_value=zone)
        cloudfs.Zones(self._global_admin).delete(self._zone_name)
        self._global_admin.cloudfs.zones.get.assert_called_once_with(self._zone_name)
        self._global_admin.execute.assert_called_once_with('', 'deleteZones', [self._zone_id])

    @staticmethod
    def _get_add_zone_response(rc):
        response = Object()
        response.rc = rc
        return response

    def _get_zone_param(self, policy_type=PolicyType.SELECT, description=None, zone_id=None):
        param = Object()
        param._classname = "SaveZoneParam"  # pylint: disable=protected-access
        param.basicInfo = Object()
        param.basicInfo._classname = 'ZoneBasicInfo'  # pylint: disable=protected-access
        param.basicInfo.name = self._zone_name
        param.basicInfo.policyType = policy_type
        param.basicInfo.description = description
        param.basicInfo.zoneId = zone_id
        param.delta = Object()
        param.delta._classname = 'ZoneDelta'  # pylint: disable=protected-access
        param.delta.devicesDelta = Object()
        param.delta.devicesDelta._classname = 'ZoneDeviceDelta'  # pylint: disable=protected-access
        param.delta.devicesDelta.added = []
        param.delta.devicesDelta.removed = []

        return param

    @staticmethod
    def _get_zones_display_info_empty_response():
        response = Object()
        response.objects = []
        return response

    def _get_zones_display_info_response(self):
        response = Object()
        zone = Object()
        zone.zoneId = self._zone_id
        response.objects = [zone]
        return response
        