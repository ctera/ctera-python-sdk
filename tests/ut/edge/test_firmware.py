from pathlib import Path
from unittest import mock

from cterasdk.exceptions import CTERAException
from cterasdk.common import Object
from cterasdk.edge import firmware
from tests.ut.edge import base_edge


class TestEdgeFirmware(base_edge.BaseEdgeTest):
    _task_pointer = '/status/upload'
    _status_msg_success = 'Success'
    _status_msg_failure = 'Failure'
    _file_path = str(Path(__file__).resolve())

    def test_upgrade_success(self):
        for reboot in [True, False]:
            for wait_for_reboot in [True, False]:
                self._test_upgrade_success(reboot, wait_for_reboot)

    def _test_upgrade_success(self, reboot, wait_for_reboot):
        self._init_filer(
            get_response=self._get_task_status_cmd_response(firmware.UploadTaskStatus.COMPLETE),
            form_data_response=self._get_upgrade_cmd_response(0)
        )
        self._filer.power.reboot = mock.MagicMock()
        firmware.Firmware(self._filer).upgrade(TestEdgeFirmware._file_path, reboot=reboot, wait_for_reboot=wait_for_reboot)
        self._filer.api.form_data.assert_called_with(
            'proc/firmware',
            dict(
                name='upload',
                firmware=mock.ANY
            )
        )
        self._filer.api.get.assert_called_with(TestEdgeFirmware._task_pointer)
        if reboot:
            self._filer.power.reboot.assert_called_with(wait=wait_for_reboot)
        else:
            self._filer.power.reboot.assert_not_called()

    def test_upgrade_upload_failed(self):
        self._init_filer(
            form_data_response=self._get_upgrade_cmd_response(1)
        )
        with self.assertRaises(CTERAException) as error:
            firmware.Firmware(self._filer).upgrade(TestEdgeFirmware._file_path)
        self._filer.api.form_data.assert_called_with(
            'proc/firmware',
            dict(
                name='upload',
                firmware=mock.ANY
            )
        )
        self._filer.api.get.assert_not_called()
        self.assertEqual(error.exception.message, 'Failed to upload the new firmware')
        self.assertEqual(error.exception.path, TestEdgeFirmware._file_path)

    def test_upgrade_process_failed(self):
        self._init_filer(
            get_response=self._get_task_status_cmd_response(firmware.UploadTaskStatus.FAIL),
            form_data_response=self._get_upgrade_cmd_response(0)
        )
        with self.assertRaises(CTERAException) as error:
            firmware.Firmware(self._filer).upgrade(TestEdgeFirmware._file_path)
        self._filer.api.form_data.assert_called_with(
            'proc/firmware',
            dict(
                name='upload',
                firmware=mock.ANY
            )
        )
        self._filer.api.get.assert_called_with(TestEdgeFirmware._task_pointer)
        self.assertEqual(error.exception.message, 'Filer failed to receive the new firmware - Failure')

    @staticmethod
    def _get_upgrade_cmd_response(rc):
        o = Object()
        o.rc = rc
        o.taskPointer = TestEdgeFirmware._task_pointer
        return o

    @staticmethod
    def _get_task_status_cmd_response(status):
        o = Object()
        o.status = status
        o.statusMessage = TestEdgeFirmware._status_msg_success if \
            status == firmware.UploadTaskStatus.COMPLETE else TestEdgeFirmware._status_msg_failure
        return o
