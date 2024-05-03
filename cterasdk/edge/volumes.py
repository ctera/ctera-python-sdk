import logging

from ..lib.task_manager_base import TaskError
from .enum import VolumeStatus
from ..common import Object
from ..exceptions import CTERAException, InputError
from ..lib import track
from .base_command import BaseCommand


class Volumes(BaseCommand):
    """ Edge Filer Volumes configuration APIs """

    def get(self, name=None):
        """
        Get Volume. If a volume name was not passed as an argument, a list of all storage volumes will be retrieved
        :param str,optional name: Name of the volume
        """
        return self._edge.api.get('/config/storage/volumes' + ('' if name is None else ('/' + name)))

    def add(self, name, size=None, filesystem='xfs', device=None, passphrase=None):
        """
        Add a Volume.

        :param str name: Name of the new volume
        :param int,optional size: Size of the new volume, defaults to the device's size
        :param str,optional filesystem: Filesystem to use, defaults to xfs
        :param str,optional device: Name of the device to use for the new volume, can be left as None if there's only one device available
        :param str,optional passphrase: Passphrase for the volume

        :return: Edge Filer response
        """
        storage_devices = self._devices()
        device_name, device_size = Volumes._device_volume(device, storage_devices)
        storage_volume_size = Volumes._volume_size(size, device_name, device_size)
        filesystem = Volumes._volume_filesystem(filesystem)

        param = Object()
        param.name = name
        param.device = device_name
        param.size = storage_volume_size
        param.fileSystemType = filesystem

        if passphrase is not None:
            param.encrypted = True
            param.encPassphrase = passphrase

        logging.getLogger('cterasdk.edge').info(
            'Creating volume. %s',
            {'name': name, 'device': device_name, 'size': size, 'filesystem': filesystem, 'passphrase': passphrase}
        )

        ref = '/status/storage/volumes/' + param.name + '/status'

        response = self._edge.api.add('/config/storage/volumes', param)

        status = track(
            self._edge,
            ref,
            [VolumeStatus.Ok],
            [VolumeStatus.Formatting],
            [VolumeStatus.Mounting, VolumeStatus.Checking, VolumeStatus.Repairing], [VolumeStatus.Corrupted, VolumeStatus.Unknown]
        )

        logging.getLogger('cterasdk.edge').info('Volume created. %s', {'name': name, 'size': size, 'status': status})

        return response

    def modify(self, name, size=None):
        """
        Modify an existing volume

        :param int,optional size: New size of the volume, if not set, the size will not change
        :return: Edge Filer response
        """
        if size is None:
            return Object()

        try:
            volume = self.get(name)
        except CTERAException as error:
            raise CTERAException('Failed to get the volume', error)

        volume.size = size
        try:
            response = self._edge.api.put('/config/storage/volumes/' + name, volume)
            logging.getLogger('cterasdk.edge').info("Volume modified. %s", {'volume': volume.name})
            return response
        except CTERAException as error:
            msg = "Failed to modify volume."
            logging.getLogger('cterasdk.edge').error(msg)
            raise CTERAException(msg, error)

    def delete(self, name):
        """
        Delete a volume

        :param str name: Name of the volume to delete
        """
        self._wait_pending_mount(name)
        try:
            logging.getLogger('cterasdk.edge').info('Deleting volume. %s', {'name': name})

            response = self._edge.api.delete('/config/storage/volumes/' + name)

            logging.getLogger('cterasdk.edge').info("Volume deleted. %s", {'name': name})

            return response
        except CTERAException as error:
            logging.getLogger('cterasdk.edge').error("Volume deletion failed. %s", {'name': name})
            raise CTERAException('Volume deletion falied', error)

    def delete_all(self):
        """ Delete all volumes """
        self._wait_pending_filesystem_mounts()

        volumes = self._edge.api.get('/config/storage/volumes')
        volume_count = len(volumes)
        if volume_count > 0:
            for volume in volumes:
                self.delete(volume.name)
        else:
            logging.getLogger('cterasdk.edge').info('No volumes found.')

    def _devices(self):
        arrays = self._edge.api.get('/status/storage/arrays')
        drives = self._edge.api.get('/status/storage/disks')

        ctera_devices = {}
        for array in arrays:
            ctera_devices[array.name] = array.availableCapacity

        for drive in drives:
            ctera_devices[drive.name] = drive.availableCapacity

        if len(ctera_devices) == 0:
            logging.getLogger('cterasdk.edge').error('Could not find any drives or arrays.')

            raise CTERAException('Could not find any drives or arrays')

        return ctera_devices

    @staticmethod
    def _device_volume(device_name, ctera_devices):
        if device_name is not None:
            device_size = ctera_devices.get(device_name)
            if device_size is not None:
                logging.getLogger('cterasdk.edge').debug('Found drive. %s', {'name': device_name, 'size': device_size})
                return (device_name, device_size)

            device_names = [k for k, v in ctera_devices.items()]
            logging.getLogger('cterasdk.edge').error('Invalid device name. %s', {'name': device_name})
            raise InputError('Invalid device name', device_name, device_names)

        if len(ctera_devices) == 1:
            device_name, device_size = ctera_devices.popitem()
            logging.getLogger('cterasdk.edge').debug('Found drive. %s', {'name': device_name, 'size': device_size})
            return device_name, device_size

        device_names = [k for k, v in ctera_devices.items()]
        logging.getLogger('cterasdk.edge').error('You must specify a drive or an array name. %s', {'options': device_names})
        raise CTERAException('You must specify a drive or an array name', None, options=device_names)

    @staticmethod
    def _volume_size(size, device_name, device_size):
        if size is not None:
            if size > device_size:
                logging.getLogger('cterasdk.edge').error('You cannot exceed the available storage capacity. %s',
                                                         {'size': size, 'free_size': device_size})
                raise InputError("You cannot exceed the available storage capacity", size, device_size)
            return size

        if device_size > 0:
            logging.getLogger('cterasdk.edge').info('You did not specify a volume size.')
            logging.getLogger('cterasdk.edge').info('Allocating available storage capacity. %s',
                                                    {'name': device_name, 'free_size': device_size})
            return device_size

        logging.getLogger('cterasdk.edge').error('Insufficient storage space. %s', {'name': device_name})
        raise CTERAException('Insufficient storage space', None, device=device_name, free_size=device_size)

    @staticmethod
    def _volume_filesystem(filesystem):
        filesystem = filesystem.lower()
        if filesystem in ['xfs', 'next3', 'ext3']:
            return filesystem
        raise InputError('Invalid file system type', filesystem, ['xfs', 'next3', 'ext3'])

    def _wait_pending_filesystem_mounts(self):
        logging.getLogger('cterasdk.edge').debug('Checking for pending mount tasks.')

        tasks = self._edge.tasks.running()
        for mount in tasks:
            if mount.name.startswith('Mounting'):
                self._wait_mount(mount.id)

    def _wait_pending_mount(self, volume):
        logging.getLogger('cterasdk.edge').debug('Checking for pending mount tasks. %s', {'volume': volume})

        tasks = self._edge.tasks.by_name(' '.join(['Mounting', volume, 'file system']))
        for mount in tasks:
            self._wait_mount(mount.id)

    def _wait_mount(self, tid):
        try:
            self._edge.tasks.wait(tid)
        except TaskError:
            logging.getLogger('cterasdk.edge').debug('Failed mounting volume. %s', {'tid': tid})
