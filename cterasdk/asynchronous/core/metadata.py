import asyncio
import logging


from .base_command import BaseCommand
from .iterator import CursorAsyncIterator
from ...common import Object
from ...convert import tojsondict
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
        Get Metadata Changes for Selected Cloud Drive Folders

        :param list[CloudFSFolderFindingHelper],optional drives: List of Cloud Drive folders, defaults to all cloud drive folders.
        :param str,optional cursor: Cursor
        """
        param = Object()
        param.max_results = 30
        param.folder_ids = []
        if cursor:
            param.cursor = cursor
        if drives:
            for drive in drives:
                async for drive in await self._core.cloudfs.drives.find(drive.name, drive.owner, include=['uid']):
                    param.folder_ids.append(drive.uid)
        logging.getLogger().info('Listing updates.')
        return iterator(self._core, '/metadata/list', param)

    async def changes(self, cursor, timeout=None):
        """
        Check for Changes

        :param str cursor: Cursor
        :param int,optional cursor: Timeout

        :returns: ``True`` if changes are available for this ``cursor``, ``False`` otherwise
        :rtype: bool
        """
        param = Object()
        param.cursor = cursor
        param.timeout = timeout if timeout else 10000
        logging.getLogger().info('Checking for updates. %s', {'timeout': timeout})
        return (await self._core.v2.api.post('/metadata/longpoll', param)).changes


class Service(BaseCommand):
    """Change Notification Service"""

    def __init__(self, core):
        super().__init__(core)
        self._event = asyncio.Event()

    def start(self, cursor=None, on_event=None):
        """
        Start Service.

        :param str,optional cursor: Start enumerating changes from cursor.
        :param callback,optional on_event: An asynchronous callback function that to handle incoming events.
         The callback should accept one argument:
          - event (dict): The event to be processed
        """
        return asyncio.create_task(run_forever(self._core, self._event, cursor, on_event))

    def stop(self):
        """
        Stop Service.
        """
        self._event.set()


async def run_forever(core, event, cursor, on_event):
    while True:
        if event.is_set():
            logging.getLogger().info('Shutdown event received.')
            break
        else:
            if cursor is None or await core.metadata.changes(cursor):
                iterator = await core.metadata.get(cursor=cursor)
                tasks = [asyncio.create_task(on_event(tojsondict(event))) async for event in iterator]
                if tasks:
                    logging.getLogger().info('Creating tasks. %s', {'events': len(tasks)})
                    asyncio.gather(*tasks)
                    logging.getLogger().info('Tasks created.')
                cursor = iterator.cursor
                logging.getLogger().info('Next Cursor. %s', {'cursor': cursor})
