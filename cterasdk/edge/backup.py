import logging

from ..common import Object
from ..exceptions import CTERAException
from ..exceptions.backup import NotFound, AttachEncrypted, IncorrectPassphrase, ClocksOutOfSync
from .enum import BackupConfStatusID
from .base_command import BaseCommand
from .directorytree import DirectoryTree


logger = logging.getLogger('cterasdk.edge')


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


class Backup(BaseCommand):
    """ Edge Filer backup configuration APIs """

    def __init__(self, edge):
        super().__init__(edge)
        self.files = BackupFiles(self._edge)

    def configure(self, passphrase=None):
        """
        Edge Filer backup configuration

        :param str,optional passphrase: Passphrase for the backup, defaults to None
        """
        logger.info('Configuring cloud backup.')

        try:
            settings = self._attach(passphrase)
        except NotFound:
            settings = self._create_folder(passphrase)

        self._configure_backup_settings(settings)

        logger.info('Cloud backup configuration completed successfully.')

    def is_configured(self):
        """
        Is Backup configured

        :return bool: True if backup is configured, else False
        """
        backup_status = self._edge.api.get('/proc/backup/backupStatus')
        return backup_status.serviceStatus.id == BackupConfStatusID.Attached

    def start(self):
        """ Start backup """
        logger.info("Starting cloud backup.")
        self._edge.api.execute("/status/sync", "start")

    def suspend(self):
        """ Suspend backup """
        logger.info("Suspending cloud backup.")
        self._edge.api.execute("/status/sync", "pause")

    def unsuspend(self):
        """ Unsuspend backup """
        logger.info("Suspending cloud backup.")
        self._edge.api.execute("/status/sync", "resume")

    def _attach(self, sharedSecret):
        try:
            logger.debug('Attaching to a backup folder.')
            settings = self._attach_folder()
        except AttachEncrypted as param:
            logger.debug('Attaching to an encrypted backup folder.')
            settings = self._attach_encrypted_folder(param.encryptedFolderKey, param.passPhraseSalt, sharedSecret)
            settings.encryptionMode = param.encryptionMode
        logger.debug('Successfully attached to a backup folder.')

        return settings

    def _attach_folder(self):
        task = self._edge.api.execute('/status/services', 'attachFolder')
        return self._attach_response(task)

    def _attach_encrypted_folder(self, encryptedFolderKey, passPhraseSalt, sharedSecret):
        param = Object()
        param.encryptedFolderKey = encryptedFolderKey
        param.passPhraseSalt = passPhraseSalt
        param.sharedSecret = sharedSecret

        task = self._edge.api.execute('/status/services', 'attachEncryptedFolder', param)
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
            logger.debug('Could not find an existing backup folder.')
            raise NotFound()

        if rc == AttachRC.IsEncrypted:
            raise AttachEncrypted(response.encryptionMode, response.encryptedFolderKey, response.passPhraseSalt)

        if rc == AttachRC.CheckCodeInCorrect:
            logger.error('Incorrect passphrase.')
            raise IncorrectPassphrase()

        if rc == AttachRC.ClocksOutOfSync:
            logger.error('Intializing backup failed. Clocks are out of sync (rc=%s).', rc)
            raise ClocksOutOfSync()

        if rc == AttachRC.InternalServerError:
            logger.error('Attach failed (rc=%s).', rc)
        elif rc == AttachRC.PermissionDenied:
            logger.error('Attach failed (rc=%s).', rc)
        else:
            logger.error('Unknown error (rc=%s)', rc)
        raise CTERAException(f'Failed to attach to backup folder (rc={rc}).')

    def _create_folder(self, passphrase):
        param = Object()
        if passphrase is not None:
            logger.debug('Creting a passphrase-encrypted backup folder.')
            param.encryptionMode = EncryptionMode.Secret
            param.sharedSecret = passphrase
        else:
            logger.debug('Creating a backup folder.')
            param.encryptionMode = EncryptionMode.Recoverable

        task = self._edge.api.execute('/status/services', 'createFolder', param)
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
            logger.debug('Backup folder created successfully.')
            param = Object()
            param.sharedSecret = response.sharedSecret
            param.passPhraseSalt = response.passPhraseSalt
            return param

        if rc == CreateFolderRC.InternalServerError:
            logger.error('Backup folder creation failed (rc=%s).', rc)
        elif rc == CreateFolderRC.PermissionDenied:
            logger.error('Backup folder creation failed (rc=%s).', rc)
        elif rc == CreateFolderRC.FolderAlreadyExists:
            return None
        raise CTERAException(f'Failed to create backup folder (rc={rc})')

    def _wait(self, task):
        task = self._edge.tasks.wait(task)
        return task.result

    def _configure_backup_settings(self, param):
        backup_settings = self._edge.api.get('/config/backup')
        if not backup_settings:
            backup_settings = self._edge.api.defaults('BackupSettings')

        backup_settings.encryptionMode = param.encryptionMode
        backup_settings.sharedSecret = param.sharedSecret
        backup_settings.passPhraseSalt = param.passPhraseSalt

        logger.debug('Configuring backup settings.')

        self._edge.api.put('/config/backup', backup_settings)


class BackupFiles(BaseCommand):

    ALL_FILES = 'All File Types'

    def unselect_all(self):
        """ Unselect all files from backup """
        backup_config = self._fetch_backup_config(BackupFiles.ALL_FILES)
        logger.info('Unselecting all files from backup.')
        directory_tree = DirectoryTree(backup_config.directoryTree)
        directory_tree.unselect_all()
        backup_config.directoryTree = directory_tree.root
        return self._update_backup_config(backup_config)

    def _fetch_backup_config(self, name=None):
        backup_configs = self._edge.api.get('/config/backup/backupPolicy/includeSets')
        if name:
            for backup_config in backup_configs:
                if backup_config.name == name:
                    logger.info('Found backup config: %s', name)
                    return backup_config
            logger.error('Could not find backup config: %s', name)
            raise CTERAException(f'Could not find backup config: {name}')
        return backup_configs

    def _update_backup_config(self, backup_config):
        return self._edge.api.put(f'/config/backup/backupPolicy/includeSets/{backup_config._uuid}', backup_config)  # pylint: disable=W0212
