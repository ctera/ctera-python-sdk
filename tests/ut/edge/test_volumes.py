from unittest import mock

from cterasdk import exceptions
from cterasdk.common import Object
from cterasdk.edge.enum import VolumeStatus
from cterasdk.edge import volumes
from tests.ut.edge import base_edge


class TestEdgeVolumes(base_edge.BaseEdgeTest):

    _drive_1 = 'SATA-1'
    _drive_2 = 'SATA-2'
    _drive_size = 81920
    _mount_task_1 = (1, 'Task 1')
    _mount_task_2 = (2, 'Task 2')

    def setUp(self):
        super().setUp()
        self._volume_1_name = 'localcache'
        self._volume_2_name = 'logs'
        self._volumes = [self._volume_1_name, self._volume_2_name]
        self._volume_passphrase = 'password'
        self._mount_id = 'task id'

    def test_get_all_volumes(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = volumes.Volumes(self._filer).get()
        self._filer.api.get.assert_called_once_with('/config/storage/volumes')
        self.assertEqual(ret, get_response)

    def test_get_volume(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = volumes.Volumes(self._filer).get(self._volume_1_name)
        self._filer.api.get.assert_called_once_with('/config/storage/volumes/' + self._volume_1_name)
        self.assertEqual(ret, get_response)

    def test_add_volume_default_args_single_device_success(self):
        add_response = 'Success'
        self._init_filer(add_response=add_response)
        self._filer.api.get = mock.MagicMock(side_effect=TestEdgeVolumes._mock_no_arrays_single_drive)
        track_volume_creation_status_mock = self.patch_call("cterasdk.edge.volumes.track")
        ret = volumes.Volumes(self._filer).add(self._volume_1_name)
        self._filer.api.get.assert_has_calls(
            [
                mock.call('/status/storage/arrays'),
                mock.call('/status/storage/disks')
            ]
        )
        track_volume_creation_status_mock.assert_called_once_with(self._filer,
                                                                  '/status/storage/volumes/' + self._volume_1_name + '/status',
                                                                  [VolumeStatus.Ok],
                                                                  [VolumeStatus.Formatting],
                                                                  [VolumeStatus.Mounting, VolumeStatus.Checking, VolumeStatus.Repairing],
                                                                  [VolumeStatus.Corrupted, VolumeStatus.Unknown])
        self._filer.api.add.assert_called_once_with('/config/storage/volumes', mock.ANY)
        expected_param = self._get_add_volume_param(device=TestEdgeVolumes._drive_1, size=TestEdgeVolumes._drive_size)
        actual_param = self._filer.api.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, add_response)

    def test_add_encrypted_volume_default_args_single_device_success(self):
        add_response = 'Success'
        self._init_filer(add_response=add_response)
        self._filer.api.get = mock.MagicMock(side_effect=TestEdgeVolumes._mock_no_arrays_single_drive)
        track_volume_creation_status_mock = self.patch_call("cterasdk.edge.volumes.track")
        ret = volumes.Volumes(self._filer).add(self._volume_1_name, passphrase=self._volume_passphrase)
        self._filer.api.get.assert_has_calls(
            [
                mock.call('/status/storage/arrays'),
                mock.call('/status/storage/disks')
            ]
        )
        track_volume_creation_status_mock.assert_called_once_with(self._filer,
                                                                  '/status/storage/volumes/' + self._volume_1_name + '/status',
                                                                  [VolumeStatus.Ok],
                                                                  [VolumeStatus.Formatting],
                                                                  [VolumeStatus.Mounting, VolumeStatus.Checking, VolumeStatus.Repairing],
                                                                  [VolumeStatus.Corrupted, VolumeStatus.Unknown])
        self._filer.api.add.assert_called_once_with('/config/storage/volumes', mock.ANY)
        expected_param = self._get_add_volume_param(device=TestEdgeVolumes._drive_1,
                                                    size=TestEdgeVolumes._drive_size,
                                                    passphrase=self._volume_passphrase)
        actual_param = self._filer.api.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, add_response)

    def test_add_volume_no_devices(self):
        self._init_filer()
        self._filer.api.get = mock.MagicMock(side_effect=TestEdgeVolumes._mock_no_devices)
        with self.assertRaises(exceptions.CTERAException) as error:
            volumes.Volumes(self._filer).add(self._volume_1_name)
        self._filer.api.get.assert_has_calls(
            [
                mock.call('/status/storage/arrays'),
                mock.call('/status/storage/disks')
            ]
        )
        self.assertEqual('Could not find any drives or arrays', error.exception.message)

    def test_add_volume_invalid_device_name(self):
        self._init_filer()
        self._filer.api.get = mock.MagicMock(side_effect=TestEdgeVolumes._mock_no_arrays_multiple_drive)
        with self.assertRaises(exceptions.InputError) as error:
            volumes.Volumes(self._filer).add(self._volume_1_name, device='Invalid device name')
        self._filer.api.get.assert_has_calls(
            [
                mock.call('/status/storage/arrays'),
                mock.call('/status/storage/disks')
            ]
        )
        self.assertEqual('Invalid device name', error.exception.message)

    def test_add_volume_must_specify_device_name(self):
        self._init_filer()
        self._filer.api.get = mock.MagicMock(side_effect=TestEdgeVolumes._mock_no_arrays_multiple_drive)
        with self.assertRaises(exceptions.CTERAException) as error:
            volumes.Volumes(self._filer).add(self._volume_1_name)
        self._filer.api.get.assert_has_calls(
            [
                mock.call('/status/storage/arrays'),
                mock.call('/status/storage/disks')
            ]
        )
        self.assertEqual('You must specify a drive or an array name', error.exception.message)

    def test_add_volume_with_device_success(self):
        add_response = 'Success'
        self._init_filer(add_response=add_response)
        self._filer.api.get = mock.MagicMock(side_effect=TestEdgeVolumes._mock_no_arrays_multiple_drive)
        track_volume_creation_status_mock = self.patch_call("cterasdk.edge.volumes.track")
        ret = volumes.Volumes(self._filer).add(self._volume_1_name, device=TestEdgeVolumes._drive_1)
        self._filer.api.get.assert_has_calls(
            [
                mock.call('/status/storage/arrays'),
                mock.call('/status/storage/disks')
            ]
        )
        track_volume_creation_status_mock.assert_called_once_with(self._filer,
                                                                  '/status/storage/volumes/' + self._volume_1_name + '/status',
                                                                  [VolumeStatus.Ok],
                                                                  [VolumeStatus.Formatting],
                                                                  [VolumeStatus.Mounting, VolumeStatus.Checking, VolumeStatus.Repairing],
                                                                  [VolumeStatus.Corrupted, VolumeStatus.Unknown])
        self._filer.api.add.assert_called_once_with('/config/storage/volumes', mock.ANY)
        expected_param = self._get_add_volume_param(device=TestEdgeVolumes._drive_1, size=TestEdgeVolumes._drive_size)
        actual_param = self._filer.api.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, add_response)

    def test_add_volume_exceeding_drive_size(self):
        self._init_filer()
        self._filer.api.get = mock.MagicMock(side_effect=TestEdgeVolumes._mock_no_arrays_single_drive)
        with self.assertRaises(exceptions.InputError) as error:
            volumes.Volumes(self._filer).add(self._volume_1_name, size=999999999)
        self._filer.api.get.assert_has_calls(
            [
                mock.call('/status/storage/arrays'),
                mock.call('/status/storage/disks')
            ]
        )
        self.assertEqual('You cannot exceed the available storage capacity', error.exception.message)

    def test_delete_volume_success(self):
        delete_response = 'Success'
        self._init_filer(delete_response=delete_response)
        self._filer.tasks.by_name = mock.MagicMock(return_value=[TestEdgeVolumes._get_pending_mount_task(self._mount_id)])
        self._filer.tasks.wait = mock.MagicMock()
        ret = volumes.Volumes(self._filer).delete(self._volume_1_name)
        self._filer.tasks.by_name.assert_called_once_with(' '.join(['Mounting', self._volume_1_name, 'file system']))
        self._filer.tasks.wait.assert_called_once_with(self._mount_id)
        self._filer.api.delete.assert_called_once_with('/config/storage/volumes/' + self._volume_1_name)
        self.assertEqual(ret, delete_response)

    def test_delete_volume_raise(self):
        self._init_filer()
        self._filer.api.delete = mock.MagicMock(side_effect=exceptions.CTERAException())
        self._filer.tasks.by_name = mock.MagicMock(return_value=[])
        with self.assertRaises(exceptions.CTERAException) as error:
            volumes.Volumes(self._filer).delete(self._volume_1_name)
        self._filer.tasks.by_name.assert_called_once_with(' '.join(['Mounting', self._volume_1_name, 'file system']))
        self._filer.api.delete.assert_called_once_with('/config/storage/volumes/' + self._volume_1_name)
        self.assertEqual('Volume deletion failed', error.exception.message)

    def test_delete_all_volume_success(self):
        delete_response = 'Success'
        self._init_filer(get_response=self._get_volumes_response_param(), delete_response=delete_response)
        self._filer.tasks.running = mock.MagicMock(return_value=TestEdgeVolumes._get_pending_mount_tasks())
        self._filer.tasks.by_name = mock.MagicMock()
        self._filer.tasks.wait = mock.MagicMock()
        volumes.Volumes(self._filer).delete_all()
        self._filer.api.get.assert_called_once_with('/config/storage/volumes')
        self._filer.tasks.running.assert_called_once()
        self._filer.api.delete.assert_has_calls(
            [
                mock.call('/config/storage/volumes/' + self._volume_1_name),
                mock.call('/config/storage/volumes/' + self._volume_2_name)
            ]
        )

    def test_modify_volume_success(self):
        before_volume_size = 1000
        after_volume_size = 9999
        put_response = 'Success'
        self._init_filer(get_response=TestEdgeVolumes._get_volume_response(self._volume_1_name, before_volume_size),
                         put_response=put_response)
        ret = volumes.Volumes(self._filer).modify(self._volume_1_name, 9999)
        self._filer.api.get.assert_called_once_with('/config/storage/volumes/' + self._volume_1_name)
        self._filer.api.put.assert_called_once_with('/config/storage/volumes/' + self._volume_1_name, mock.ANY)
        expected_param = TestEdgeVolumes._get_volume_response(self._volume_1_name, after_volume_size)
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, put_response)

    def test_modify_volume_not_found(self):
        self._init_filer()
        self._filer.api.get = mock.MagicMock(side_effect=exceptions.CTERAException())
        with self.assertRaises(exceptions.CTERAException) as error:
            volumes.Volumes(self._filer).modify(self._volume_1_name, 9999)
        self._filer.api.get.assert_called_once_with('/config/storage/volumes/' + self._volume_1_name)
        self.assertEqual('Failed to get the volume', error.exception.message)

    @staticmethod
    def _get_volume_response(name, size):
        param = Object()
        param.name = name
        param.size = size
        return param

    def _get_volumes_response_param(self):
        storage_volumes = []
        for volume_name in self._volumes:
            param = Object()
            param.name = volume_name
            storage_volumes.append(param)
        return storage_volumes

    def test_delete_no_volumes_found(self):
        self._init_filer(get_response=[])
        self._filer.tasks.running = mock.MagicMock(return_value=[])
        volumes.Volumes(self._filer).delete_all()
        self._filer.api.get.assert_called_once_with('/config/storage/volumes')

    @staticmethod
    def _get_pending_mount_tasks():
        mount_id, task_name = TestEdgeVolumes._mount_task_1
        task_1 = TestEdgeVolumes._get_pending_mount_task(mount_id, task_name)
        mount_id, task_name = TestEdgeVolumes._mount_task_2
        task_2 = TestEdgeVolumes._get_pending_mount_task(mount_id, task_name)
        return [task_1, task_2]

    @staticmethod
    def _get_pending_mount_task(mount_id=None, name=None):
        param = Object()
        if mount_id:
            param.id = mount_id
        if name:
            param.name = name
        return param

    @staticmethod
    def _get_drive(name, capacity):
        param = Object()
        param.name = name
        param.availableCapacity = capacity
        return param

    def _get_add_volume_param(self, device=None, size=None, passphrase=None):
        param = Object()
        param.name = self._volume_1_name
        if device:
            param.device = device
        if size:
            param.size = size
        param.fileSystemType = 'xfs'
        if passphrase:
            param.encrypted = True
            param.encPassphrase = passphrase
        return param

    @staticmethod
    def _mock_no_devices(path):
        if path == '/status/storage/arrays':
            return []
        if path == '/status/storage/disks':
            return []
        return None

    @staticmethod
    def _mock_no_arrays_single_drive(path):
        if path == '/status/storage/arrays':
            return []
        if path == '/status/storage/disks':
            return [TestEdgeVolumes._get_drive(TestEdgeVolumes._drive_1, TestEdgeVolumes._drive_size)]
        return None

    @staticmethod
    def _mock_no_arrays_multiple_drive(path):
        if path == '/status/storage/arrays':
            return []
        if path == '/status/storage/disks':
            return [TestEdgeVolumes._get_drive(TestEdgeVolumes._drive_1, TestEdgeVolumes._drive_size),
                    TestEdgeVolumes._get_drive(TestEdgeVolumes._drive_2, TestEdgeVolumes._drive_size)]
        return None
