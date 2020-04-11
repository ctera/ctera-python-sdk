import logging

from . import taskmgr as TaskManager
from ..common import Object
from ..exception import CTERAException
from .enum import BackupConfStatusID
from .base_command import BaseCommand


class AttachRC:
    OK = 'OK'
    NotFound = 'NotFound'
    IsEncrypted = 'IsEncrypted'
    CheckCodeInCorrect = 'CheckCodeInCorrect'
    ClocksOutOfSync = 'ClocksOutOfSync'
    InternalServerError = 'InternalServerError'
    PermissionDenied = 'PermissionDenied'


class CreateFolderRC:
    OK = 'OK'
    InternalServerError = 'InternalServerError'
    PermissionDenied = 'PermissionDenied'
    FolderAlreadyExists = 'FolderAlreadyExists'


class EncryptionMode:
    """
    Encryption mode types

    :ivar str Recoverable: Recoverable key encryption mode
    :ivar str Secret: Secret key encryption mode
    """
    Recoverable = 'RecoverableKeyEncryption'
    Secret = 'SecretKeyEncryption'


class NotFound(CTERAException):
    """ Not found exception """


class AttachEncrypted(CTERAException):
    """ Attach Encrypted exception """

    def __init__(self, encryptionMode, encryptedFolderKey, passPhraseSalt):
        super().__init__()
        self.encryptionMode = encryptionMode
        self.encryptedFolderKey = encryptedFolderKey
        self.passPhraseSalt = passPhraseSalt


class IncorrectPassphrase(CTERAException):
    """ Incorrect Passphrase exception """

    def __init__(self):
        super().__init__('Incorrect passphrase')


class ClocksOutOfSync(CTERAException):
    """ Clocks Out of Sync exception """

    def __init__(self):
        super().__init__('Clocks are out of sync')


class Backup(BaseCommand):
    """ Gateway backup configuration APIs """

    def configure(self, passphrase=None):
        """
        Gateway backup configuration

        :param str,optional passphrase: Passphrase for the backup, defaults to None
        """
        logging.getLogger().info('Configuring cloud backup.')

        try:
            settings = self._attach(passphrase)
        except NotFound:
            settings = self._create_folder(passphrase)

        self._configure_backup_settings(settings)

        logging.getLogger().info('Cloud backup configuration completed successfully.')

    def is_configured(self):
        """
        Is Backup configured

        :return bool: True if backup is configured, else False
        """
        backup_status = self._gateway.get('/proc/backup/backupStatus')
        return backup_status.serviceStatus.id == BackupConfStatusID.Attached

    def start(self):
        """ Start backup """
        logging.getLogger().info("Starting cloud backup.")
        self._gateway.execute("/status/sync", "start")

    def suspend(self):
        """ Suspend backup """
        logging.getLogger().info("Suspending cloud backup.")
        self._gateway.execute("/status/sync", "pause")

    def unsuspend(self):
        """ Unsuspend backup """
        logging.getLogger().info("Suspending cloud backup.")
        self._gateway.execute("/status/sync", "resume")

    def _attach(self, sharedSecret):
        try:
            logging.getLogger().debug('Attaching to a backup folder.')
            settings = self._attach_folder()
        except AttachEncrypted as param:
            logging.getLogger().debug('Attaching to an encrypted backup folder.')
            settings = self._attach_encrypted_folder(param.encryptedFolderKey, param.passPhraseSalt, sharedSecret)
            settings.encryptionMode = param.encryptionMode
        logging.getLogger().debug('Successfully attached to a backup folder.')

        return settings

    def _attach_folder(self):
        task = self._gateway.execute('/status/services', 'attachFolder')
        return self._attach_response(task)

    def _attach_encrypted_folder(self, encryptedFolderKey, passPhraseSalt, sharedSecret):
        param = Object()
        param.encryptedFolderKey = encryptedFolderKey
        param.passPhraseSalt = passPhraseSalt
        param.sharedSecret = sharedSecret

        task = self._gateway.execute('/status/services', 'attachEncryptedFolder', param)
        return self._attach_response(task)

    def _attach_response(self, task):
        response = self._wait(task)
        return Backup._process_attach_response(response)

    @staticmethod
    def _process_attach_response(response):
        rc = response.attachFolderRC

        if rc == AttachRC.OK:
            param = Object()
            if hasattr(response, 'encryptionMode'):
                param.encryptionMode = response.encryptionMode
            param.sharedSecret = response.sharedSecret
            param.passPhraseSalt = response.passPhraseSalt
            return param

        if rc == AttachRC.NotFound:
            logging.getLogger().debug('Could not find an existing backup folder.')
            raise NotFound()

        if rc == AttachRC.IsEncrypted:
            raise AttachEncrypted(response.encryptionMode, response.encryptedFolderKey, response.passPhraseSalt)

        if rc == AttachRC.CheckCodeInCorrect:
            logging.getLogger().error('Incorrect passphrase.')
            raise IncorrectPassphrase()

        if rc == AttachRC.ClocksOutOfSync:
            logging.getLogger().error('Intializing backup failed. Clocks are out of sync. %s', {'rc': rc})
            raise ClocksOutOfSync()

        if rc == AttachRC.InternalServerError:
            logging.getLogger().error('Attach failed. %s', {'rc': rc})
        elif rc == AttachRC.PermissionDenied:
            logging.getLogger().error('Attach failed. %s', {'rc': rc})
        else:
            logging.getLogger().error('Unknown error, %s', {'rc': rc})
        raise CTERAException('Failed to attach to backup folder', None, rc=rc)

    def _create_folder(self, passphrase):
        param = Object()
        if passphrase is not None:
            logging.getLogger().debug('Creting a passphrase-encrypted backup folder.')
            param.encryptionMode = EncryptionMode.Secret
            param.sharedSecret = passphrase
        else:
            logging.getLogger().debug('Creating a backup folder.')
            param.encryptionMode = EncryptionMode.Recoverable

        task = self._gateway.execute('/status/services', 'createFolder', param)
        settings = self._create_response(task)
        settings.encryptionMode = param.encryptionMode

        return settings

    def _create_response(self, task):
        response = self._wait(task)
        return Backup._process_create_response(response)

    @staticmethod
    def _process_create_response(response):
        rc = response.createFolderRC

        if rc == CreateFolderRC.OK:
            logging.getLogger().debug('Backup folder created successfully.')
            param = Object()
            param.sharedSecret = response.sharedSecret
            param.passPhraseSalt = response.passPhraseSalt
            return param

        if rc == CreateFolderRC.InternalServerError:
            logging.getLogger().error('Backup folder creation failed. %s', {'rc': rc})
        elif rc == CreateFolderRC.PermissionDenied:
            logging.getLogger().error('Backup folder creation failed. %s', {'rc': rc})
        elif rc == CreateFolderRC.FolderAlreadyExists:
            return None
        raise CTERAException('Failed to create backup folder', None, rc=rc)

    def _wait(self, task):
        try:
            task = TaskManager.wait(self._gateway, task)
            return task.result
        except TaskManager.TaskError:
            pass

    def _configure_backup_settings(self, param):
        backup_settings = self._gateway.get('/config/backup')
        if not backup_settings:
            backup_settings = self._gateway.get('/defaults/BackupSettings')

        backup_settings.encryptionMode = param.encryptionMode
        backup_settings.sharedSecret = param.sharedSecret
        backup_settings.passPhraseSalt = param.passPhraseSalt

        logging.getLogger().debug('Configuring backup settings.')

        self._gateway.put('/config/backup', backup_settings)
