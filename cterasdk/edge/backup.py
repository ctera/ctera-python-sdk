import logging

from . import taskmgr as TaskManager
from ..common import Object
from ..exception import CTERAException


class EncryptionMode:
    Recoverable = 'RecoverableKeyEncryption'
    Secret = 'SecretKeyEncryption'


class NotFound(CTERAException):
    pass


class AttachEncrypted(CTERAException):

    def __init__(self, encryptionMode, encryptedFolderKey, passPhraseSalt):
        super(AttachEncrypted, self).__init__()
        self.encryptionMode = encryptionMode
        self.encryptedFolderKey = encryptedFolderKey
        self.passPhraseSalt = passPhraseSalt


class IncorrectPassphrase(CTERAException):

    def __init__(self):
        super(IncorrectPassphrase, self).__init__(self, 'Incorrect passphrase')


class ClockOutOfSync(CTERAException):

    def __init__(self):
        super(ClockOutOfSync, self).__init__(self, 'Clocks are out of sync')


def configure_backup(ctera_host, passphrase):
    logging.getLogger().info('Configuring cloud backup.')

    try:
        settings = attach(ctera_host, passphrase)
    except NotFound:
        settings = create_folder(ctera_host, passphrase)

    configure_backup_settings(ctera_host, settings)

    logging.getLogger().info('Cloud backup configuration completed successfully.')


def attach(ctera_host, sharedSecret):
    try:
        logging.getLogger().debug('Attaching to a backup folder.')
        settings = attach_folder(ctera_host)
    except AttachEncrypted as param:
        logging.getLogger().debug('Attaching to an encrypted backup folder.')
        settings = attach_encrypted_folder(ctera_host, param.encryptedFolderKey, param.passPhraseSalt, sharedSecret)
        settings.encryptionMode = param.encryptionMode
    logging.getLogger().debug('Successfully attached to a backup folder.')

    return settings


def attach_folder(ctera_host):
    task = ctera_host.execute('/status/services', 'attachFolder')
    return attach_response(ctera_host, task)


def attach_encrypted_folder(ctera_host, encryptedFolderKey, passPhraseSalt, sharedSecret):
    param = Object()
    param.encryptedFolderKey = encryptedFolderKey
    param.passPhraseSalt = passPhraseSalt
    param.sharedSecret = sharedSecret

    task = ctera_host.execute('/status/services', 'attachEncryptedFolder', param)
    return attach_response(ctera_host, task)


def attach_response(ctera_host, task):
    response = wait(ctera_host, task)
    return process_attach_response(response)


def process_attach_response(response):
    rc = response.attachFolderRC

    if rc == 'OK':
        param = Object()
        if hasattr(response, 'encryptionMode'):
            param.encryptionMode = response.encryptionMode
        param.sharedSecret = response.sharedSecret
        param.passPhraseSalt = response.passPhraseSalt
        return param

    if rc == 'NotFound':
        logging.getLogger().debug('Could not find an existing backup folder.')
        raise NotFound()

    if rc == 'IsEncrypted':
        raise AttachEncrypted(response.encryptionMode, response.encryptedFolderKey, response.passPhraseSalt)

    if rc == 'CheckCodeInCorrect':
        logging.getLogger().error('Incorrect passphrase.')
        raise IncorrectPassphrase()

    if rc == 'ClocksOutOfSync':
        logging.getLogger().error('Intializing backup failed. Clocks are out of sync. %s', {'rc' : rc})
        raise ClockOutOfSync()

    if rc == 'InternalServerError':
        logging.getLogger().error('Attach failed. %s', {'rc' : rc})
    elif rc == 'PermissionDenied':
        logging.getLogger().error('Attach failed. %s', {'rc' : rc})
    else:
        logging.getLogger().error('Unknow error, %s', {'rc' : rc})
    raise CTERAException(message="Failed to Attach")


def create_folder(ctera_host, passphrase):
    param = Object()
    if passphrase is not None:
        logging.getLogger().debug('Creting a passphrase-encrypted backup folder.')
        param.encryptionMode = EncryptionMode.Secret
        param.sharedSecret = passphrase
    else:
        logging.getLogger().debug('Creating a backup folder.')
        param.encryptionMode = EncryptionMode.Recoverable

    task = ctera_host.execute('/status/services', 'createFolder', param)
    settings = create_response(ctera_host, task)
    settings.encryptionMode = param.encryptionMode

    return settings


def create_response(ctera_host, task):
    response = wait(ctera_host, task)
    return process_create_response(response)


def process_create_response(response):
    rc = response.createFolderRC

    if rc == 'OK':
        logging.getLogger().debug('Backup folder created successfully.')
        param = Object()
        param.sharedSecret = response.sharedSecret
        param.passPhraseSalt = response.passPhraseSalt
        return param

    if rc == 'InternalServerError':
        logging.getLogger().error('Backup folder creation failed. %s', {'rc' : rc})
    elif rc == 'PermissionDenied':
        logging.getLogger().error('Backup folder creation failed. %s', {'rc' : rc})
    elif rc == 'FolderAlreadyExists':
        return None
    raise CTERAException(message="Failed to Create")


def wait(ctera_host, task):
    try:
        task = TaskManager.wait(ctera_host, task)
        return task.result
    except TaskManager.TaskError:
        pass


def configure_backup_settings(ctera_host, param):
    backup_settings = ctera_host.get('/config/backup')
    if not backup_settings:
        backup_settings = ctera_host.get('/defaults/BackupSettings')

    backup_settings.encryptionMode = param.encryptionMode
    backup_settings.sharedSecret = param.sharedSecret
    backup_settings.passPhraseSalt = param.passPhraseSalt

    logging.getLogger().debug('Configuring backup settings.')

    ctera_host.put('/config/backup', backup_settings)


def start(ctera_host):
    logging.getLogger().info("Starting cloud backup.")
    ctera_host.execute("/status/sync", "start")


def suspend(ctera_host):
    logging.getLogger().info("Suspending cloud backup.")
    ctera_host.execute("/status/sync", "pause")


def unsuspend(ctera_host):
    logging.getLogger().info("Suspending cloud backup.")
    ctera_host.execute("/status/sync", "resume")
