import logging

from ..common import Object
from .files.path import CTERAPath
from .base_command import BaseCommand


class Quotas(BaseCommand):
    """ Edge Filer Local Quotas APIs """

    ALL = 0

    def enable(self, index=True):
        """
        Enable Local Quotas and Restart Cloud Sync.

        :param bool,optional index: Index all direcories, defaults to ``True``
        """
        logging.getLogger().info("Enabling Quotas.")
        self._gateway.put('/config/cloudsync/enableLocalQuota', True)
        self._gateway.sync.restart()
        if index:
            self.index(Quotas.ALL)
        logging.getLogger().info("Quotas enabled.")

    def disable(self):
        """
        Disable Local Quotas.
        """
        logging.getLogger().info("Disabling Quotas.")
        self._gateway.put('/config/cloudsync/enableLocalQuota', False)
        self._gateway.sync.restart()
        logging.getLogger().info("Quotas disabled.")

    def index(self, fid):
        """
        Index Directory Size

        :param int fid: Cloud Drive Folder ID
        """
        param = Object()
        param.folderID = fid
        param.ignoreOvl = True
        message = 'Indexing directory. %s' if fid != 0 else 'Indexing all directories. %s'
        logging.getLogger().info(message, {'id': fid})
        return self._gateway.execute('/config/cloudsync', 'markFolderForScan', param)

    def reset(self):
        """
        Reset Local Quotas and Index All Directories. Ensure Telnet daemon is enabled.
        """
        filepath = '/tmp/freshquotadb'
        logging.getLogger().info('Creating file. %s', {'path': filepath})
        self._gateway.shell.run_command(f'touch {filepath}')
        self._gateway.sync.restart()
        self.index(Quotas.ALL)

    def status(self):
        """
        Get Status
        """
        return self._gateway.get('/proc/localQuota')

    def _validate_directory(self, path):
        self._gateway.ls(path)
        path = CTERAPath(path, '/').parts()
        return (path[3], '/'.join(path[4:]))

    def set_quota(self, path, limit, enforce=True):
        """
        Set quota

        :param str path: Folder path
        :param int limit: Quota in Megabytes (MB)
        :param bool,optional enforce: Enforce quota, defaults to ``True``
        """
        cloud_drive, relative_path = self._validate_directory(path)
        param = Object()
        param.folderId = None
        param.relPath = relative_path
        param.quotaLimit = limit
        param.enforceQuota = enforce
        return self._gateway.execute('/config/cloudsync/subFoldersLocalQuota', 'editSubfolderQuotaConfig', param)

    def del_quota(self, path):
        """
        Remove quota

        :param str path: Folder path
        """
        cloud_drive, relative_path = self._validate_directory(path)
        param = Object()
        param.folderId = None
        param.relPath = relative_path
        return self._gateway.execute('/config/cloudsync/subFoldersLocalQuota', 'delSubfolderQuotaConfig', param)
