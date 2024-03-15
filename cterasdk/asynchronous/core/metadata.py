import asyncio
import logging


from .base_command import BaseCommand
from .iterator import CursorAsyncIterator
from ...common import Object
from ...convert import tojsonstr, fromjsonstr
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
        List Changes.

        :param list[CloudFSFolderFindingHelper],optional drives: List of Cloud Drive folders, defaults to all cloud drive folders.
        :param str,optional cursor: Cursor
        """
        param = Object()
        param.max_results = 30
        param.folder_ids = []
        param.cursor = cursor
        if drives:
            for drive in drives:
                async for drive in await self._core.cloudfs.drives.find(drive.name, drive.owner, include=['uid']):
                    param.folder_ids.append(drive.uid)
        logging.getLogger().info('Listing updates.')
        return iterator(self._core, '/metadata/list', param)

    async def changes(self, cursor, timeout=None):
        """
        Check for Changes.

        :param str cursor: Cursor
        :param int,optional cursor: Timeout

        :returns: ``True`` if changes are available for this ``cursor``, ``False`` otherwise
        :rtype: bool
        """
        param = Object()
        param.cursor = cursor
        param.timeout = timeout if timeout else 10000
        logging.getLogger().info('Checking for updates. %s', {'timeout': param.timeout})
        return (await self._core.v2.api.post('/metadata/longpoll', param)).changes

    async def ancestors(self, descendant):
        """
        Get Ancestors.

        :param str descendant: Event, formatted as a JSON document
        :returns: Sorted List of Ancestors
        :rtype: list[cterasdk.common.object.Object]
        """
        descendant = fromjsonstr(descendant)
        param = Object()
        param.folder_id = descendant.folder_id
        param.guid = descendant.guid
        logging.getLogger().info('Getting ancestors. %s', {'guid': param.guid, 'folder_id': param.folder_id})
        return self._ancestry(descendant, await self._core.v2.api.post('/metadata/ancestors', param))

    def _ancestry(self, descendant, ancestors):
        """
        Sorted Ancestry.
        """
        ancestry_mapper = {ancestor.guid: ancestor for ancestor in ancestors}
        ancestry = [descendant]

        current_ancestor = descendant
        while ancestry_mapper:
            ancestor = ancestry_mapper.pop(current_ancestor.parent_guid)
            ancestry.insert(0, ancestor)
            current_ancestor = ancestor
        return ancestry


class Service(BaseCommand):
    """Change Notification Service"""

    def __init__(self, core):
        super().__init__(core)

    def run(self, queue, cursor=None, save_cursor=None):
        """
        Start Service.

        :param asyncio.Queue queue: Event Queue.
        :param str,optional cursor: Cursor.
        :param callback,optional save_cursor: Asynchronous callback function to persist the cursor.
        """
        return asyncio.create_task(run_forever(self._core, queue, cursor, save_cursor))


async def run_forever(core, queue, cursor, save_cursor):
    """
    Change Notification Service.

    :param cterasdk.objects.data.DataServices core: Data Services object
    :param asyncio.Queue queue: Queue to process events.
    :param str cursor: Cursor.
    :param callback save_cursor: Asynchronous callback function to persist the cursor.
    """
    logging.getLogger().info('Running Service.')
    try:
        while True:
            if cursor is None or await core.metadata.changes(cursor):
                events = await core.metadata.get(cursor=cursor)
                await enqueue_events(events, queue)
                logging.getLogger().debug('Joining Queue.')
                await queue.join()
                logging.getLogger().debug('Completed Processing.')
                cursor = events.cursor
                await persist_cursor(save_cursor, cursor)
    except asyncio.CancelledError:
        logging.getLogger().info('Cancelling Task.')


async def persist_cursor(save_cursor, cursor):
    """
    Persist Cursor.

    :param callback save_cursor: Asynchronous callback function to persist the cursor.
    :param str cursor: Cursor
    """
    logging.getLogger().debug('Saving Cursor.')
    await save_cursor(cursor)
    logging.getLogger().debug('Cursor Saved.')


async def enqueue_events(events, queue):
    """
    Enqueue Events.

    :param cterasdk..Queue queue: Event Queue.
    :param cterasdk.asynchronous.core.iterator.CursorAsyncIterator events: Event Iterator.
    """
    async for event in events:
        logging.getLogger().debug('Enqueuing Event.')
        await queue.put(tojsonstr(event, False, False))
        logging.getLogger().debug('Enqueued Event.')