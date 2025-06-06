import logging

from .directorytree import DirectoryTree

from .enum import OperationMode
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


class Cache(BaseCommand):
    """ Edge Filer cache configuration """

    def enable(self):
        """ Enable caching """
        logger.info('Enabling caching.')
        self._set_operation_mode(OperationMode.CachingGateway)

    def disable(self):
        """ Disable caching """
        logger.info('Disabling caching.')
        self._set_operation_mode(OperationMode.Disabled)

    def force_eviction(self):
        """ Force eviction """
        logger.info("Starting file eviction.")
        self._edge.api.execute("/config/cloudsync", "forceExecuteEvictor", None)
        logger.info("Eviction started.")

    def is_enabled(self):
        return self._edge.api.get('/config/cloudsync/cloudExtender/operationMode') == OperationMode.CachingGateway

    def _set_operation_mode(self, mode):
        self._edge.api.put('/config/cloudsync/cloudExtender/operationMode', mode)
        logger.info('Device opreation mode changed. %s', {'mode': mode})

    def pin(self, path):
        """
        Pin a folder

        :param str path: Directory path
        """
        directory_tree = self._fetch_pinning_config()
        logger.info('Pinning folder. %s', {'path': path})
        directory_tree.include_folder(path)
        self._update_pinning_config(directory_tree)

    def pin_exclude(self, path):
        """
        Exclude a sub-folder from a pinned folder

        :param str path: Directory path
        """
        directory_tree = self._fetch_pinning_config()
        logger.info('Excluding sub-folder. %s', {'path': path})
        directory_tree.exclude_folder(path)
        self._update_pinning_config(directory_tree)

    def remove_pin(self, path):
        """
        Remove a pin from a previously pinned folder

        :param str path: Directory path
        """
        directory_tree = self._fetch_pinning_config()
        logger.info('Removing pin from previously pinned folder. %s', {'path': path})
        directory_tree.remove_selection(path)
        self._update_pinning_config(directory_tree)

    def pin_all(self):
        """ Pin all folders """
        directory_tree = self._fetch_pinning_config()
        logger.info('Pinning all folders.')
        directory_tree.select_all()
        self._update_pinning_config(directory_tree)

    def unpin_all(self):
        """ Remove all folder pins """
        directory_tree = self._fetch_pinning_config()
        logger.info('Removing all folder pins.')
        directory_tree.unselect_all()
        self._update_pinning_config(directory_tree)

    def _fetch_pinning_config(self):
        root = self._edge.api.get('/config/cloudsync/cloudExtender/selectedFolders')
        return DirectoryTree(root)

    def _update_pinning_config(self, directory_tree):
        self._edge.api.put('/config/cloudsync/cloudExtender/selectedFolders', directory_tree.root)

    def pin_recursive(self, path):
        """
        Pin a folder and all its subfolders recursively

        :param str path: Directory path
        """
        directory_tree = self._fetch_pinning_config()
        logger.info('Recursively pinning folder and all subfolders. %s', {'path': path})
        directory_tree.include_folder_recursive(path)
        self._update_pinning_config(directory_tree)

    def unpin_recursive(self, path):
        """
        Unpin a folder and all its subfolders recursively

        :param str path: Directory path
        """
        directory_tree = self._fetch_pinning_config()
        logger.info('Recursively unpinning folder and all subfolders. %s', {'path': path})
        directory_tree.exclude_folder_recursive(path)
        self._update_pinning_config(directory_tree)
