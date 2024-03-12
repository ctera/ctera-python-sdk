import asyncio

from .base_command import BaseCommand
from .iterator import CursorAsyncIterator
from ...common import Object
from ...lib import CursorResponse, Command


def iterator(core, path, param):
    """
    Create iterator

    :param cterasdk.objects.core.Portal core: Portal object
    :param str path: URL Path
    :param cterasdk.common.object.Object param: Object parameter

    :returns: Iterator
    """
    async def execute(core, path, param):
        return CursorResponse(await core.v2.api.post(path, param))

    callback_function = Command(execute, core, path)
    return CursorAsyncIterator(callback_function, param)


class Metadata(BaseCommand):
    """CTERA Portal Metadata Connector APIs"""

    def __init__(self, core):
        super().__init__(core)
        self.service = Service(core)

    async def get(self, drives=None, *, cursor=None):
        """
        List All Metadata Changes for Selected Cloud Drive Folders

        :param list[CloudFSFolderFindingHelper],optional drives: List of Cloud Drive folders, defaults to all cloud drive folders.
        :param str,optional cursor: Cursor
        """
        param = Object()
        param.max_results = 2000
        param.folder_ids = []
        if cursor:
            param.cursor = cursor
        if drives:
            for drive in drives:
                async for drive in await self._core.cloudfs.drives.find(drive.name, drive.owner, include=['uid']):
                    param.folder_ids.append(drive.uid)
        return iterator(self._core, '/metadata/list', param)

    async def execute(self, callback):
        return [asyncio.create_task(callback(e)) async for e in await self.get()]


class Service(BaseCommand):

    def start(self):
        pass

    def stop(self):
        pass