import logging

from ..common import Object
from ..exceptions import CTERAException
from .enum import BackupConfStatusID
from .base_command import BaseCommand
from .directorytree import DirectoryTree


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
    """ Edge Filer backup configuration APIs """

    def __init__(self, edge):
        super().__init__(edge)
        self.files = BackupFiles(self._edge)

    def configure(self, passphrase=None):
        """
        Edge Filer backup configuration

        :param str,optional passphrase: Passphrase for the backup, defaults to None
        """
        logging.getLogger('cterasdk.edge').info('Configuring cloud backup.')

        try:
            settings = self._attach(passphrase)
        except NotFound:
            settings = self._create_folder(passphrase)

        self._configure_backup_settings(settings)

        logging.getLogger('cterasdk.edge').info('Cloud backup configuration completed successfully.')

    def is_configured(self):
        """
        Is Backup configured

        :return bool: True if backup is configured, else False
        """
        backup_status = self._edge.api.get('/proc/backup/backupStatus')
        return backup_status.serviceStatus.id == BackupConfStatusID.Attached

    def start(self):
        """ Start backup """
        logging.getLogger('cterasdk.edge').info("Starting cloud backup.")
        self._edge.api.execute("/status/sync", "start")

    def suspend(self):
        """ Suspend backup """
        logging.getLogger('cterasdk.edge').info("Suspending cloud backup.")
        self._edge.api.execute("/status/sync", "pause")

    def unsuspend(self):
        """ Unsuspend backup """
        logging.getLogger('cterasdk.edge').info("Suspending cloud backup.")
        self._edge.api.execute("/status/sync", "resume")

    def _attach(self, sharedSecret):
        try:
            logging.getLogger('cterasdk.edge').debug('Attaching to a backup folder.')
            settings = self._attach_folder()
        except AttachEncrypted as param:
            logging.getLogger('cterasdk.edge').debug('Attaching to an encrypted backup folder.')
            settings = self._attach_encrypted_folder(param.encryptedFolderKey, param.passPhraseSalt, sharedSecret)
            settings.encryptionMode = param.encryptionMode
        logging.getLogger('cterasdk.edge').debug('Successfully attached to a backup folder.')

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
            logging.getLogger('cterasdk.edge').debug('Could not find an existing backup folder.')
            raise NotFound()

        if rc == AttachRC.IsEncrypted:
            raise AttachEncrypted(response.encryptionMode, response.encryptedFolderKey, response.passPhraseSalt)

        if rc == AttachRC.CheckCodeInCorrect:
            logging.getLogger('cterasdk.edge').error('Incorrect passphrase.')
            raise IncorrectPassphrase()

        if rc == AttachRC.ClocksOutOfSync:
            logging.getLogger('cterasdk.edge').error('Intializing backup failed. Clocks are out of sync. %s', {'rc': rc})
            raise ClocksOutOfSync()

        if rc == AttachRC.InternalServerError:
            logging.getLogger('cterasdk.edge').error('Attach failed. %s', {'rc': rc})
        elif rc == AttachRC.PermissionDenied:
            logging.getLogger('cterasdk.edge').error('Attach failed. %s', {'rc': rc})
        else:
            logging.getLogger('cterasdk.edge').error('Unknown error, %s', {'rc': rc})
        raise CTERAException('Failed to attach to backup folder', None, rc=rc)

    def _create_folder(self, passphrase):
        param = Object()
        if passphrase is not None:
            logging.getLogger('cterasdk.edge').debug('Creting a passphrase-encrypted backup folder.')
            param.encryptionMode = EncryptionMode.Secret
            param.sharedSecret = passphrase
        else:
            logging.getLogger('cterasdk.edge').debug('Creating a backup folder.')
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
            logging.getLogger('cterasdk.edge').debug('Backup folder created successfully.')
            param = Object()
            param.sharedSecret = response.sharedSecret
            param.passPhraseSalt = response.passPhraseSalt
            return param

        if rc == CreateFolderRC.InternalServerError:
            logging.getLogger('cterasdk.edge').error('Backup folder creation failed. %s', {'rc': rc})
        elif rc == CreateFolderRC.PermissionDenied:
            logging.getLogger('cterasdk.edge').error('Backup folder creation failed. %s', {'rc': rc})
        elif rc == CreateFolderRC.FolderAlreadyExists:
            return None
        raise CTERAException('Failed to create backup folder', None, rc=rc)

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

        logging.getLogger('cterasdk.edge').debug('Configuring backup settings.')

        self._edge.api.put('/config/backup', backup_settings)


class BackupFiles(BaseCommand):

    ALL_FILES = 'All File Types'

    def unselect_all(self):
        """ Unselect all files from backup """
        backup_config = self._fetch_backup_config(BackupFiles.ALL_FILES)
        logging.getLogger('cterasdk.edge').info('Unselecting all files from backup.')
        directory_tree = DirectoryTree(backup_config.directoryTree)
        directory_tree.unselect_all()
        backup_config.directoryTree = directory_tree.root
        return self._update_backup_config(backup_config)

    def _fetch_backup_config(self, name=None):
        backup_configs = self._edge.api.get('/config/backup/backupPolicy/includeSets')
        if name:
            for backup_config in backup_configs:
                if backup_config.name == name:
                    logging.getLogger('cterasdk.edge').info('Found backup config. %s', {'name': name})
                    return backup_config
            logging.getLogger('cterasdk.edge').error('Could not find backup config. %s', {'name': name})
            raise CTERAException('Could not find backup config', None, name=name)
        return backup_configs

    def _update_backup_config(self, backup_config):
        return self._edge.api.put(f'/config/backup/backupPolicy/includeSets/{backup_config._uuid}', backup_config)  # pylint: disable=W0212
