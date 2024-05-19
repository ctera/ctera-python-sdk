import asyncio
import logging


from .types import Event
from .base_command import BaseCommand
from ...common import Object
from ...lib import CursorResponse
from ...exceptions import ClientResponseException


class Notifications(BaseCommand):
    """CTERA Portal Notification Service APIs"""

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
        logging.getLogger('cterasdk.metadata.connector').debug('Listing updates.')
        return CursorResponse(await self._core.v2.api.post('/metadata/list', param))

    async def _create_parameter(self, drives, cursor):
        param = Object()
        param.max_results = 2000
        param.folder_ids = []
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
        :param int,optional timeout: Timeout

        :returns: ``True`` if changes are available for this ``cursor``, ``False`` otherwise
        :rtype: bool
        """
        param = Object()
        param.cursor = cursor
        param.timeout = timeout if timeout else 10000
        logging.getLogger('cterasdk.metadata.connector').debug('Checking for updates. %s', {'timeout': param.timeout})
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
        logging.getLogger('cterasdk.metadata.connector').debug('Getting ancestors. %s', {'guid': param.guid, 'folder_id': param.folder_id})
        try:
            return await self._core.v2.api.post('/metadata/ancestors', param)
        except ClientResponseException:
            logging.getLogger('cterasdk.metadata.connector').error('Could not retrieve ancestors. %s',
                                                                   {'folder_id': param.folder_id, 'guid': param.guid})
            raise


class Service(BaseCommand):
    """Change Notification Service"""

    def __init__(self, core):
        super().__init__(core)
        self._promises = []

    def run(self, client_queue, save_cursor, *, cloudfolders=None, cursor=None):
        """
        Start Service.

        :param asyncio.Queue client_queue: Queue.
        :param callback save_cursor: Asynchronous callback function to persist the cursor.
        :param list[CloudFSFolderFindingHelper] cloudfolders: List of Cloud Drive folders.
        :param str,optional cursor: Cursor.
        """
        server_queue = asyncio.Queue(maxsize=3)
        retrieve = asyncio.create_task(retrieve_events(server_queue, self._core, cloudfolders, cursor))
        forward = asyncio.create_task(forward_events(server_queue, client_queue, save_cursor))
        self._promises = [retrieve, forward]

    async def stop(self):
        """Stop Service"""
        for promise in self._promises:
            promise.cancel()
            try:
                await promise
            except asyncio.CancelledError:
                pass
        self._promises.clear()


async def retrieve_events(server_queue, core, cloudfolders, cursor):
    """
    Retrieval Service.

    :param asyncio.Queue server_queue: Queue.
    :param cterasdk.objects.data.DataServices core: Data Services object.
    :param list[CloudFSFolderFindingHelper] cloudfolders: List of Cloud Drive folders.
    :param str cursor: Cursor
    """
    logging.getLogger('cterasdk.metadata.connector').debug('Event Retrieval Service.')
    last_response = LastResponse(cursor)
    try:
        while True:
            try:
                if last_response.cursor is None or last_response.more or \
                        await core.notifications.changes(last_response.cursor):
                    response = await core.notifications.get(cloudfolders, last_response.cursor)
                    if response.objects:
                        await server_queue.put(response)
                    last_response = response
            except ConnectionError as error:
                await on_connection_error(error)
            except TimeoutError:
                logging.getLogger('cterasdk.metadata.connector').debug('Request timed out. Retrying.')
    except asyncio.CancelledError:
        logging.getLogger('cterasdk.metadata.connector').debug('Cancelling Event Retrieval.')


async def forward_events(server_queue, client_queue, save_cursor):
    """
    Change Notification Service.

    :param asyncio.Queue server_queue: Server queue.
    :param asyncio.Queue client_queue: Client queue.
    :param callback save_cursor: Callback function to persist the cursor.
    """
    logging.getLogger('cterasdk.metadata.connector').debug('Event Forwarder Service.')
    try:
        while True:
            batch = await server_queue.get()
            await enqueue_events(batch.objects, client_queue)
            await process_events(client_queue)
            await persist_cursor(save_cursor, batch.cursor)
    except asyncio.CancelledError:
        logging.getLogger('cterasdk.metadata.connector').debug('Cancelling Event Forwarding.')


async def enqueue_events(events, queue):
    """
    Enqueue Events.

    :param asyncio.Queue queue: Event Queue.
    :param cterasdk.asynchronous.core.iterator.CursorAsyncIterator events: Event Iterator.
    """
    for event in events:
        logging.getLogger('cterasdk.metadata.connector').debug('Enqueuing Event.')
        await queue.put(Event.from_server_object(event))
        logging.getLogger('cterasdk.metadata.connector').debug('Enqueued Event.')


async def process_events(queue):
    """
    Process Events.

    :param asyncio.Queue queue: Queue.
    """
    logging.getLogger('cterasdk.metadata.connector').debug('Joining Queue.')
    await queue.join()
    logging.getLogger('cterasdk.metadata.connector').debug('Completed Processing.')


async def persist_cursor(save_cursor, cursor):
    """
    Persist Cursor.

    :param callback save_cursor: Asynchronous callback function to persist the cursor.
    :param str cursor: Cursor
    """
    logging.getLogger('cterasdk.metadata.connector').debug("Persisting Cursor. Calling function: '%s'", save_cursor.__name__)
    try:
        await save_cursor(cursor)
        logging.getLogger('cterasdk.metadata.connector').debug("Called Persist Cursor Function.")
    except Exception:  # pylint: disable=broad-exception-caught
        logging.getLogger('cterasdk.metadata.connector').error("An error occurred while trying to persist cursor. Function: '%s'",
                                                               save_cursor.__name__)


async def on_connection_error(error):
    seconds = 5
    logging.getLogger('cterasdk.metadata.connector').error('Connection error. Reason: %s.', str(error))
    logging.getLogger('cterasdk.metadata.connector').debug("Retrying in %s seconds.", seconds)
    await asyncio.sleep(seconds)


class LastResponse:

    def __init__(self, cursor):
        self._cursor = cursor

    @property
    def more(self):
        return False

    @property
    def objects(self):
        return []

    @property
    def cursor(self):
        return self._cursor
