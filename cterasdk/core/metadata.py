import logging

from .base_command import BaseCommand
from ..common import Object

from ..lib import CursorIterator, CursorResponse, Command


def iterator(core, path, param):
    """
    Create iterator

    :param cterasdk.objects.core.Portal core: Portal object
    :param str path: URL Path
    :param cterasdk.common.object.Object param: Object parameter
    
    :returns: Iterator
    """
    def execute(core, path, param):
        return CursorResponse(core.v2api.post(path, param))
    
    callback_function = Command(execute, core, path)
    return CursorIterator(callback_function, param)


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
        param.max_results = 2000
        param.folder_ids = []
        if drives:
            param.folder_ids = [self._core.cloudfs.drives.find(drive.name, drive.owner, include=['uid']).uid for drive in drives]
        return iterator(self._core, '/metadata/list', param)