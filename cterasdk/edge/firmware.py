from ..lib import FileSystem
from ..exceptions import CTERAException
from .base_command import BaseCommand


class UploadTaskStatus():
    IN_PROGRESS = 0
    COMPLETE = 1
    FAIL = -1


class Firmware(BaseCommand):
    """ Edge Filer Firmware upgrade API """

    def __init__(self, edge):
        super().__init__(edge)
        self._filesystem = FileSystem.instance()

    def upgrade(self, file_path, reboot=True, wait_for_reboot=True):
        """
        Upgrade the Filer firmware with the provided file

        :param str file_path: Path to the local file to upload
        :param bool,optional reboot: Perform reboot after uploading the new firmware, defaults to True
        :param bool,optional wait_for_reboot: Wait for reboot to complete (if reboot is performed), defaults to True
        """
        upload_task_info = self._upload_firmware(file_path)
        if upload_task_info.rc != 0:
            raise CTERAException(message='Failed to upload the new firmware', path=file_path)
        self._wait_for_completion(upload_task_info.taskPointer)
        if reboot:
            self._edge.power.reboot(wait=wait_for_reboot)

    def _upload_firmware(self, file_path):
        self._filesystem.get_local_file_info(file_path)
        with open(file_path, 'rb') as fd:
            return self._edge.api.form_data(
                'proc/firmware',
                dict(
                    name='upload',
                    firmware=fd
                )
            )

    def _wait_for_completion(self, task_pointer):
        while True:
            task_status = self._edge.api.get(task_pointer)
            is_running = task_status.status == UploadTaskStatus.IN_PROGRESS
            if not is_running:
                if task_status.status == UploadTaskStatus.COMPLETE:
                    return
                raise CTERAException(
                    message=f'Filer failed to receive the new firmware - {task_status.statusMessage}',
                    instance=task_status
                )
