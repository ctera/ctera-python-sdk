import asyncio
import logging


from .types import Event
from .base_command import BaseCommand
from .iterator import CursorAsyncIterator
from ...common import Object
from ...lib import CursorResponse, Command
from ...exceptions import ClientResponseException


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

    async def get(self, cloudfolders=None, cursor=None):
        """
        List Changes.

        :param list[CloudFSFolderFindingHelper],optional cloudfolders: List of Cloud Drive folders, defaults to all cloud drive folders.
        :param str,optional cursor: Cursor

        :returns: An asynchronous iterator
        :rtype: cterasdk.asynchronous.core.iterator.CursorAsyncIterator
        """
        param = await self._create_parameter(cloudfolders, cursor)
        logging.getLogger().info('Listing updates.')
        return iterator(self._core, '/metadata/list', param)

    async def _create_parameter(self, drives, cursor):
        param = Object()
        param.max_results = 2000
        param.folder_ids = []
        if cursor is not None:
            logging.getLogger().info('Cursor Received. Listing from Cursor.')
        param.cursor = cursor
        if drives:
            for drive in drives:
                async for drive in await self._core.cloudfs.drives.find(drive.name, drive.owner, include=['uid']):
                    param.folder_ids.append(drive.uid)
        return param

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

        :param cterasdk.asynchronous.core.types.Event descendant: Event
        :returns: Sorted List of Ancestors
        :rtype: list[cterasdk.common.object.Object]
        """
        param = Object()
        param.folder_id = descendant.folder_id
        param.guid = descendant.guid
        logging.getLogger().info('Getting ancestors. %s', {'guid': param.guid, 'folder_id': param.folder_id})
        try:
            return Metadata._ancestry(descendant, await self._core.v2.api.post('/metadata/ancestors', param))
        except ClientResponseException:
            logging.getLogger().error('Could not retrieve ancestors. %s', {'folder_id': param.folder_id, 'guid': param.guid})
            raise

    @staticmethod
    def _ancestry(descendant, ancestors):
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

    def run(self, queue, save_cursor, *, cloudfolders=None, cursor=None):
        """
        Start Service.

        :param asyncio.Queue queue: Event Queue.
        :param callback save_cursor: Asynchronous callback function to persist the cursor.
        :param list[CloudFSFolderFindingHelper] cloudfolders: List of Cloud Drive folders.
        :param str,optional cursor: Cursor.
        """
        return asyncio.create_task(run_forever(self._core, queue, save_cursor, cloudfolders, cursor))


async def run_forever(core, queue, save_cursor, drives, cursor):
    """
    Change Notification Service.

    :param cterasdk.objects.data.DataServices core: Data Services object
    :param asyncio.Queue queue: Queue to process events.
    :param list[CloudFSFolderFindingHelper] drives: List of Cloud Drive folders.
    :param str cursor: Cursor.
    :param callback save_cursor: Asynchronous callback function to persist the cursor.
    """
    logging.getLogger().info('Running Service.')
    try:
        while True:
            try:
                if cursor is None or await core.metadata.changes(cursor):
                    events = await core.metadata.get(drives, cursor)
                    await enqueue_events(events, queue)
                    await process_events(queue)
                    cursor = events.cursor
                    await persist_cursor(save_cursor, cursor)
            except ConnectionError as error:
                await on_connection_error(error)
            except TimeoutError:
                logging.getLogger().warning("Request timed out. Retrying.")
    except asyncio.CancelledError:
        logging.getLogger().info('Cancelling Task.')


async def enqueue_events(events, queue):
    """
    Enqueue Events.

    :param asyncio.Queue queue: Event Queue.
    :param cterasdk.asynchronous.core.iterator.CursorAsyncIterator events: Event Iterator.
    """
    async for event in events:
        logging.getLogger().debug('Enqueuing Event.')
        await queue.put(Event.from_server_object(event))
        logging.getLogger().debug('Enqueued Event.')


async def process_events(queue):
    """
    Process Events.

    :param asyncio.Queue queue: Queue.
    """
    logging.getLogger().debug('Joining Queue.')
    await queue.join()
    logging.getLogger().debug('Completed Processing.')


async def persist_cursor(save_cursor, cursor):
    """
    Persist Cursor.

    :param callback save_cursor: Asynchronous callback function to persist the cursor.
    :param str cursor: Cursor
    """
    logging.getLogger().debug("Persisting Cursor. Calling function: '%s'", save_cursor.__name__)
    try:
        await save_cursor(cursor)
        logging.getLogger().debug("Called Persist Cursor Function.")
    except Exception:  # pylint: disable=broad-exception-caught
        logging.getLogger().error("An error occurred while trying to persist cursor. Function: '%s'", save_cursor.__name__)


async def on_connection_error(error):
    seconds = 5
    logging.getLogger().error('Connection error. Reason: %s.', str(error))
    logging.getLogger().info("Retrying in %s seconds.", seconds)
    await asyncio.sleep(seconds)
