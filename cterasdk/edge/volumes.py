from . import taskmgr as TaskManager

from .enum import VolumeStatus

from ..common import Object

from ..exception import CTERAException, InputError

from ..lib import track

import logging

def add(CTERAHost, name, size, filesystem, device, passphrase):
    
    storage_devices = devices(CTERAHost)
    
    device_name, device_size = device_volume(device, storage_devices)
    
    storage_volume_size = volume_size(size, device_name, device_size)
    
    filesystem = volume_filesystem(filesystem)
    
    param = Object()
    
    param.name      = name
    
    param.device    = device_name
    
    param.size      = storage_volume_size
    
    param.fileSystemType = filesystem
    
    if passphrase != None:
        
        param.encrypted     = True
        
        param.encPassphrase = passphrase
    
    logging.getLogger().info('Creating volume. {0}'.format({'name' : name, 'device' : device_name, 'size' : size, 'filesystem' : filesystem, 'passphrase' : passphrase}))
    
    ref = '/status/storage/volumes/' + param.name + '/status'

    response = CTERAHost.add('/config/storage/volumes', param)
    
    status = track(CTERAHost, ref, [VolumeStatus.Ok], [VolumeStatus.Formatting], [VolumeStatus.Mounting, VolumeStatus.Checking, VolumeStatus.Repairing], [VolumeStatus.Corrupted, VolumeStatus.Unknown])

    logging.getLogger().info('Volume created. {0}'.format({'name' : name, 'size' : size, 'status' : status}))

    return response
    
def devices(CTERAHost):
    
    arrays  = CTERAHost.get('/status/storage/arrays')
    
    drives  = CTERAHost.get('/status/storage/disks')
    
    devices = {}
    
    for array in arrays:
        
        devices[array.name] = array.availableCapacity
        
    for drive in drives:
        
        devices[drive.name] = drive.availableCapacity
        
    device_count = len(devices)
    
    if not device_count > 0:
        
        logging.getLogger().error('Could not find any drives or arrays.')
        
        raise CTERAException('Could not find any drives or arrays')
        
    return devices

def device_volume(device_name, devices):
    
    if device_name != None:
        
        device_size = devices.get(device_name)
        
        if device_size != None:
            
            logging.getLogger().debug('Found drive. {0}'.format({'name' : device_name, 'size' : device_size}))
            
            return (device_name, device_size)
        
        else:
            
            device_names = [ k for k,v in devices.items() ]
            
            logging.getLogger().error('Invalid device name. {0}'.format({'name' : device_name}))
            
            raise InputError('Invalid device name', device_name, device_names)
        
    else:
        
        if len(devices) == 1:
            
            device_name, device_size = devices.popitem()
            
            logging.getLogger().debug('Found drive. {0}'.format({'name' : device_name, 'size' : device_size}))
            
            return device_name, device_size
        
        else:
            
            device_names = [ k for k,v in devices.items() ]
        
            logging.getLogger().error('You must specify a drive or an array name. {0}'.format({'options' : device_names}))

            raise CTERAException('You must specify a drive or an array name', None, options = device_names)
            
def volume_size(size, device_name, device_size):
    
    if size != None:
        
        if size > device_size:
            
            logging.getLogger().error('You cannot exceed the available storage capacity. {0}'.format({'size' : size, 'free_size' : device_size}))
            
            raise InputError("You cannot exceed the available storage capacity", size, device_size)
            
        else:
            
            return size
        
    else:
        
        if device_size > 0:
            
            logging.getLogger().warn('You did not specify a volume size.')
            
            logging.getLogger().warn('Allocating available storage capacity. {0}'.format({'name' : device_name, 'free_size' : device_size}))
            
            return device_size
            
        else:
            
            logging.getLogger().error('Insufficient storage space. {0}'.format({'name' : device_name}))
            
            raise CTERAException('Insufficient storage space', None, device = device_name, free_size = device_size)
            
def volume_filesystem(filesystem):
    
    filesystem = filesystem.lower()
    
    if filesystem in ['xfs', 'next3', 'ext3']:
        
        return filesystem

    else:
        
        raise InputError('Invalid file system type', filesystem, ['xfs', 'next3', 'ext3'])

def delete(ctera_host, name):
    
    wait_pending_mount(ctera_host, name)
    
    try:
        
        logging.getLogger().info('Deleting volume. {0}'.format({'name' : name}))

        response = ctera_host.delete('/config/storage/volumes/' + name)

        logging.getLogger().info("Volume deleted. {0}".format({'name' : name}))
        
        return response

    except CTERAException as error:

        logging.getLogger().error("Volume deletion failed. {0}".format({'name' : name}))

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
    
    logging.getLogger().debug('Checking for pending mount tasks. {0}'.format({'volume' : volume}))
    
    tasks = TaskManager.by_name(CTERAHost, ' '.join(['Mounting', volume, 'file system']))
    
    for mount in tasks:
        
        wait_mount(CTERAHost, mount.id)

def wait_mount(CTERAHost, tid):
    
    try:
            
        TaskManager.wait(CTERAHost, tid)

    except TaskManager.TaskError as error:

        logging.getLogger().debug('Failed mounting volume. {0}'.format({'volume' : volume}))
    
    