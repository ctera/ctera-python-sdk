import logging

from . import taskmgr as TaskManager
from .enum import VolumeStatus
from ..common import Object
from ..exception import CTERAException, InputError
from ..lib import track


def add(CTERAHost, name, size, filesystem, device, passphrase):
    storage_devices = devices(CTERAHost)
    device_name, device_size = device_volume(device, storage_devices)
    storage_volume_size = volume_size(size, device_name, device_size)
    filesystem = volume_filesystem(filesystem)

    param = Object()
    param.name = name
    param.device = device_name
    param.size = storage_volume_size
    param.fileSystemType = filesystem

    if passphrase is not None:
        param.encrypted = True
        param.encPassphrase = passphrase

    logging.getLogger().info(
        'Creating volume. %s',
        {'name' : name, 'device' : device_name, 'size' : size, 'filesystem' : filesystem, 'passphrase' : passphrase}
    )

    ref = '/status/storage/volumes/' + param.name + '/status'

    response = CTERAHost.add('/config/storage/volumes', param)

    status = track(
        CTERAHost,
        ref,
        [VolumeStatus.Ok],
        [VolumeStatus.Formatting],
        [VolumeStatus.Mounting, VolumeStatus.Checking, VolumeStatus.Repairing], [VolumeStatus.Corrupted, VolumeStatus.Unknown]
    )

    logging.getLogger().info('Volume created. %s', {'name' : name, 'size' : size, 'status' : status})

    return response


def devices(CTERAHost):
    arrays = CTERAHost.get('/status/storage/arrays')
    drives = CTERAHost.get('/status/storage/disks')

    ctera_devices = {}
    for array in arrays:
        ctera_devices[array.name] = array.availableCapacity

    for drive in drives:
        ctera_devices[drive.name] = drive.availableCapacity

    if len(ctera_devices) == 0:
        logging.getLogger().error('Could not find any drives or arrays.')

        raise CTERAException('Could not find any drives or arrays')

    return ctera_devices


def device_volume(device_name, ctera_devices):
    if device_name is not None:
        device_size = ctera_devices.get(device_name)
        if device_size is not None:
            logging.getLogger().debug('Found drive. %s', {'name' : device_name, 'size' : device_size})
            return (device_name, device_size)

        device_names = [k for k, v in ctera_devices.items()]
        logging.getLogger().error('Invalid device name. %s', {'name' : device_name})
        raise InputError('Invalid device name', device_name, device_names)

    if len(ctera_devices) == 1:
        device_name, device_size = ctera_devices.popitem()
        logging.getLogger().debug('Found drive. %s', {'name' : device_name, 'size' : device_size})
        return device_name, device_size

    device_names = [k for k, v in ctera_devices.items()]
    logging.getLogger().error('You must specify a drive or an array name. %s', {'options' : device_names})
    raise CTERAException('You must specify a drive or an array name', None, options=device_names)


def volume_size(size, device_name, device_size):
    if size is not None:
        if size > device_size:
            logging.getLogger().error('You cannot exceed the available storage capacity. %s', {'size' : size, 'free_size' : device_size})
            raise InputError("You cannot exceed the available storage capacity", size, device_size)
        return size

    if device_size > 0:
        logging.getLogger().warning('You did not specify a volume size.')
        logging.getLogger().warning('Allocating available storage capacity. %s', {'name' : device_name, 'free_size' : device_size})
        return device_size

    logging.getLogger().error('Insufficient storage space. %s', {'name' : device_name})
    raise CTERAException('Insufficient storage space', None, device=device_name, free_size=device_size)


def volume_filesystem(filesystem):
    filesystem = filesystem.lower()
    if filesystem in ['xfs', 'next3', 'ext3']:
        return filesystem
    raise InputError('Invalid file system type', filesystem, ['xfs', 'next3', 'ext3'])


def delete(ctera_host, name):
    wait_pending_mount(ctera_host, name)
    try:
        logging.getLogger().info('Deleting volume. %s', {'name' : name})

        response = ctera_host.delete('/config/storage/volumes/' + name)

        logging.getLogger().info("Volume deleted. %s", {'name' : name})

        return response
    except CTERAException as error:
        logging.getLogger().error("Volume deletion failed. %s", {'name' : name})
        raise CTERAException('Volume deletion falied', error)


def delete_all(ctera_host):
    wait_pending_filesystem_mounts(ctera_host)

    volumes = ctera_host.get('/config/storage/volumes')
    volume_count = len(volumes)
    if volume_count > 0:
        for volume in volumes:
            delete(ctera_host, volume.name)
    else:
        logging.getLogger().info('No volumes found.')


def wait_pending_filesystem_mounts(CTERAHost):
    logging.getLogger().debug('Checking for pending mount tasks.')

    tasks = TaskManager.running(CTERAHost)
    for mount in tasks:
        if mount.name.startswith('Mounting'):
            wait_mount(CTERAHost, mount.id)


def wait_pending_mount(CTERAHost, volume):
    logging.getLogger().debug('Checking for pending mount tasks. %s', {'volume' : volume})

    tasks = TaskManager.by_name(CTERAHost, ' '.join(['Mounting', volume, 'file system']))
    for mount in tasks:
        wait_mount(CTERAHost, mount.id)


def wait_mount(CTERAHost, tid):
    try:
        TaskManager.wait(CTERAHost, tid)
    except TaskManager.TaskError:
        logging.getLogger().debug('Failed mounting volume. %s', {'tid' : tid})
