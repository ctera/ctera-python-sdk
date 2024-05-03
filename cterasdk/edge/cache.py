import logging

from .directorytree import DirectoryTree

from .enum import OperationMode
from .base_command import BaseCommand


class Cache(BaseCommand):
    """ Edge Filer cache configuration """

    def enable(self):
        """ Enable caching """
        logging.getLogger('cterasdk.edge').info('Enabling caching.')
        self._set_operation_mode(OperationMode.CachingGateway)

    def disable(self):
        """ Disable caching """
        logging.getLogger('cterasdk.edge').info('Disabling caching.')
        self._set_operation_mode(OperationMode.Disabled)

    def force_eviction(self):
        """ Force eviction """
        logging.getLogger('cterasdk.edge').info("Starting file eviction.")
        self._edge.api.execute("/config/cloudsync", "forceExecuteEvictor", None)
        logging.getLogger('cterasdk.edge').info("Eviction started.")

    def is_enabled(self):
        return self._edge.api.get('/config/cloudsync/cloudExtender/operationMode') == OperationMode.CachingGateway

    def _set_operation_mode(self, mode):
        self._edge.api.put('/config/cloudsync/cloudExtender/operationMode', mode)
        logging.getLogger('cterasdk.edge').info('Device opreation mode changed. %s', {'mode': mode})

    def pin(self, path):
        """
        Pin a folder

        :param str path: Directory path
        """
        directory_tree = self._fetch_pinning_config()
        logging.getLogger('cterasdk.edge').info('Pinning folder. %s', {'path': path})
        directory_tree.include_folder(path)
        self._update_pinning_config(directory_tree)

    def pin_exclude(self, path):
        """
        Exclude a sub-folder from a pinned folder

        :param str path: Directory path
        """
        directory_tree = self._fetch_pinning_config()
        logging.getLogger('cterasdk.edge').info('Excluding sub-folder. %s', {'path': path})
        directory_tree.exclude_folder(path)
        self._update_pinning_config(directory_tree)

    def remove_pin(self, path):
        """
        Remove a pin from a previously pinned folder

        :param str path: Directory path
        """
        directory_tree = self._fetch_pinning_config()
        logging.getLogger('cterasdk.edge').info('Removing pin from previously pinned folder. %s', {'path': path})
        directory_tree.remove_selection(path)
        self._update_pinning_config(directory_tree)

    def pin_all(self):
        """ Pin all folders """
        directory_tree = self._fetch_pinning_config()
        logging.getLogger('cterasdk.edge').info('Pinning all folders.')
        directory_tree.select_all()
        self._update_pinning_config(directory_tree)

    def unpin_all(self):
        """ Remove all folder pins """
        directory_tree = self._fetch_pinning_config()
        logging.getLogger('cterasdk.edge').info('Removing all folder pins.')
        directory_tree.unselect_all()
        self._update_pinning_config(directory_tree)

    def _fetch_pinning_config(self):
        root = self._edge.api.get('/config/cloudsync/cloudExtender/selectedFolders')
        return DirectoryTree(root)

    def _update_pinning_config(self, directory_tree):
        self._edge.api.put('/config/cloudsync/cloudExtender/selectedFolders', directory_tree.root)
