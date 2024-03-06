import logging

from .base_command import BaseCommand
from ..common import Object

from ..lib import CursorIterator, CursorResponse, Command


class Metadata(BaseCommand):
    """
    Portal Metadata Connector APIs
    """
    def all(self, drives=None):
        """
        List All Metadata Changes for Selected Cloud Drive Folders

        :param list[CloudFSFolderFindingHelper],optional drives: List of Cloud Drive folders, defaults to all cloud drive folders.
        """
        param = Object()
        param.max_results = 1
        param.folder_ids = []
        if drives:
            param.folder_ids = [self._core.cloudfs.drives.find(drive.name, drive.owner, include=['uid']) for drive in drives]
        callback = Command(self.query)
        return CursorIterator(callback, param)
    
    def query(self, param):
        response = self._core.v2api.post('/metadata/list', param)
        return CursorResponse(response)