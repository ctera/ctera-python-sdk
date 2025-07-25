import asyncio
import logging


from .types import Event
from .base_command import BaseCommand
from ...common import Object
from ...lib import CursorResponse
from ...exceptions.transport import HTTPError
from ...exceptions.notifications import NotificationsError


logger = logging.getLogger('cterasdk.notifications')


class Notifications(BaseCommand):
    """CTERA Portal Notification Service APIs"""

    def __init__(self, core):
        super().__init__(core)
        self.service = Service(core)

    async def get(self, cloudfolders=None, cursor=None, max_results=None):
        """
        List Changes.

        :param list[CloudFSFolderFindingHelper],optional cloudfolders: List of Cloud Drive folders, defaults to all cloud drive folders.
        :param str,optional cursor: Cursor
        :param int,optional max_results: Limit max results, defaults to 2000.

        :returns: An asynchronous iterator
        :rtype: cterasdk.asynchronous.core.iterator.CursorAsyncIterator
        :raises: cterasdk.exceptions.NotificationsError
        """
        param = await self._create_parameter(cloudfolders, cursor)
        param.max_results = max_results if max_results is not None else 2000
        logger.debug('Listing updates.')
        response = await self._core.v2.api.post('/metadata/list', param)
        if response is not None:
            return CursorResponse(response)
        logger.error('An error occurred while trying to retrieve notifications.')
        raise NotificationsError(cloudfolders, cursor)

    async def _create_parameter(self, cloudfolders, cursor):
        param = Object()
        param.folder_ids = []
        param.cursor = cursor
        if cloudfolders:
            if all(isinstance(cloudfolder, int) for cloudfolder in cloudfolders):
                param.folder_ids = cloudfolders
            else:
                for cloudfolder in cloudfolders:
                    async for cloudfolder in await self._core.cloudfs.drives.find(cloudfolder.name, cloudfolder.owner, include=['uid']):
                        param.folder_ids.append(cloudfolder.uid)
        return param

    async def changes(self, cursor, cloudfolders=None, timeout=None):
        """
        Check for Changes.

        :param str cursor: Cursor
        :param list[CloudFSFolderFindingHelper],optional cloudfolders: List of Cloud Drive folders, defaults to all cloud drive folders.
        :param int,optional timeout: Timeout

        :returns: ``True`` if changes are available for this ``cursor``, ``False`` otherwise
        :rtype: bool
        """
        param = Object()
        param = await self._create_parameter(cloudfolders, cursor)
        param.timeout = timeout if timeout else 10000
        logger.debug('Checking for updates. %s', {'timeout': param.timeout})
        return (await self._core.v2.api.post('/metadata/longpoll', param, **{
            'timeout': {
                'sock_read': param.timeout + 10000
            }
        })).changes

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
        logger.debug('Getting ancestors. %s', {'guid': param.guid, 'folder_id': param.folder_id})
        try:
            return await self._core.v2.api.post('/metadata/ancestors', param)
        except HTTPError:
            logger.error('Could not retrieve ancestors. %s', {'folder_id': param.folder_id, 'guid': param.guid})
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
    logger.debug('Event Retrieval Service.')
    last_response = LastResponse(cursor)
    try:
        while True:
            try:
                if last_response.cursor is None or last_response.more or \
                        await core.notifications.changes(last_response.cursor, cloudfolders):
                    response = await core.notifications.get(cloudfolders, last_response.cursor)
                    if response.objects:
                        await server_queue.put(response)
                    last_response = response
            except ConnectionError as error:
                await on_connection_error(error)
            except TimeoutError:
                logger.debug('Request timed out. Retrying.')
    except asyncio.CancelledError:
        logger.debug('Cancelling Event Retrieval.')


async def forward_events(server_queue, client_queue, save_cursor):
    """
    Change Notification Service.

    :param asyncio.Queue server_queue: Server queue.
    :param asyncio.Queue client_queue: Client queue.
    :param callback save_cursor: Callback function to persist the cursor.
    """
    logger.debug('Event Forwarder Service.')
    try:
        while True:
            batch = await server_queue.get()
            await enqueue_events(batch.objects, client_queue)
            await process_events(client_queue)
            await persist_cursor(save_cursor, batch.cursor)
    except asyncio.CancelledError:
        logger.debug('Cancelling Event Forwarding.')


async def enqueue_events(events, queue):
    """
    Enqueue Events.

    :param asyncio.Queue queue: Event Queue.
    :param cterasdk.asynchronous.core.iterator.CursorAsyncIterator events: Event Iterator.
    """
    for event in events:
        logger.debug('Enqueuing Event.')
        await queue.put(Event.from_server_object(event))
        logger.debug('Enqueued Event.')


async def process_events(queue):
    """
    Process Events.

    :param asyncio.Queue queue: Queue.
    """
    logger.debug('Joining Queue.')
    await queue.join()
    logger.debug('Completed Processing.')


async def persist_cursor(save_cursor, cursor):
    """
    Persist Cursor.

    :param callback save_cursor: Asynchronous callback function to persist the cursor.
    :param str cursor: Cursor
    """
    logger.debug("Persisting Cursor. Calling function: '%s'", save_cursor)
    try:
        await save_cursor(cursor)
        logger.debug("Called Persist Cursor Function.")
    except Exception:  # pylint: disable=broad-exception-caught
        logger.error("An error occurred while trying to persist cursor. Function: '%s'", save_cursor)


async def on_connection_error(error):
    seconds = 5
    logger.error('Connection error. Reason: %s.', str(error))
    logger.debug("Retrying in %s seconds.", seconds)
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
