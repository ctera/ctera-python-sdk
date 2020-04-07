import logging

from .directorytree import DirectoryTree

from .enum import OperationMode
from .base_command import BaseCommand


class Cache(BaseCommand):
    """ Gateway cache configuration """

    def enable(self):
        """ Enable caching """
        logging.getLogger().info('Enabling caching.')
        self._set_operation_mode(OperationMode.CachingGateway)

    def disable(self):
        """ Disable caching """
        logging.getLogger().info('Disabling caching.')
        self._set_operation_mode(OperationMode.Disabled)

    def force_eviction(self):
        """ Force eviction """
        logging.getLogger().info("Starting file eviction.")
        self._gateway.execute("/config/cloudsync", "forceExecuteEvictor", None)
        logging.getLogger().info("Eviction started.")

    def is_enabled(self):
        return self._gateway.get('/config/cloudsync/cloudExtender/operationMode') == OperationMode.CachingGateway

    def _set_operation_mode(self, mode):
        self._gateway.put('/config/cloudsync/cloudExtender/operationMode', mode)
        logging.getLogger().info('Device opreation mode changed. %s', {'mode': mode})

    def pin(self, path):
        """
        Pin a folder

        :param str path: Directory path
        """
        directory_tree = self._fetch_pinning_config()
        logging.getLogger().info('Pinning folder. %s', {'path': path})
        directory_tree.include_folder(path)
        self._update_pinning_config(directory_tree)

    def pin_exclude(self, path):
        """
        Exclude a sub-folder from a pinned folder

        :param str path: Directory path
        """
        directory_tree = self._fetch_pinning_config()
        logging.getLogger().info('Excluding sub-folder. %s', {'path': path})
        directory_tree.exclude_folder(path)
        self._update_pinning_config(directory_tree)

    def remove_pin(self, path):
        """
        Remove a pin from a previously pinned folder

        :param str path: Directory path
        """
        directory_tree = self._fetch_pinning_config()
        logging.getLogger().info('Removing pin from previously pinned folder. %s', {'path': path})
        directory_tree.remove_selection(path)
        self._update_pinning_config(directory_tree)

    def pin_all(self):
        """ Pin all folders """
        directory_tree = self._fetch_pinning_config()
        logging.getLogger().info('Pinning all folders.')
        directory_tree.select_all()
        self._update_pinning_config(directory_tree)

    def unpin_all(self):
        """ Remove all folder pins """
        directory_tree = self._fetch_pinning_config()
        logging.getLogger().info('Removing all folder pins.')
        directory_tree.unselect_all()
        self._update_pinning_config(directory_tree)

    def _fetch_pinning_config(self):
        root = self._gateway.get('/config/cloudsync/cloudExtender/selectedFolders')
        return DirectoryTree(root)

    def _update_pinning_config(self, directory_tree):
        self._gateway.put('/config/cloudsync/cloudExtender/selectedFolders', directory_tree.root)
