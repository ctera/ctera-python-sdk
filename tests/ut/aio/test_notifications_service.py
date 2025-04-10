from unittest import mock
import asyncio
import uuid
import munch
from tests.ut.aio import base_core


class TestAsyncCoreNotifications(base_core.BaseAsyncCoreTest):

    _new_cursor = uuid.uuid4().hex

    def setUp(self):
        super().setUp()
        self._get = self.patch_call('cterasdk.asynchronous.core.notifications.Notifications.get')
        self._changes = self.patch_call('cterasdk.asynchronous.core.notifications.Notifications.changes')
        self._save_cursor = mock.AsyncMock()
        self._cloudfolders = [1, 2, 3, 4]
        self._cursor = 'abcd'

    async def test_start_service(self):
        queue = asyncio.Queue()
        retrieve_events = self.patch_call('cterasdk.asynchronous.core.notifications.retrieve_events')
        forward_events = self.patch_call('cterasdk.asynchronous.core.notifications.forward_events')
        self._global_admin.notifications.service.run(queue, self._save_cursor, cloudfolders=self._cloudfolders, cursor=self._cursor)
        retrieve_events.assert_called_once_with(mock.ANY, self._global_admin, self._cloudfolders, self._cursor)
        forward_events.assert_called_once_with(mock.ANY, queue, self._save_cursor)
        self.assertEqual(retrieve_events.call_args[0][0], forward_events.call_args[0][0])
        self.assertGreater(retrieve_events.call_args[0][0].maxsize, 1)

    async def test_retrieve_events(self):
        queue = asyncio.Queue()
        self._changes.return_value = True
        self._get.return_value = TestAsyncCoreNotifications._notifications_response_object()

        # Start Service
        self._global_admin.notifications.service.run(queue, self._save_cursor, cloudfolders=self._cloudfolders, cursor=self._cursor)

        # Process Events
        await self._process_events(queue, len(self._get.return_value.objects))

        # Stop Service
        await self._global_admin.notifications.service.stop()

        self._save_cursor.assert_called_once_with(TestAsyncCoreNotifications._new_cursor)

    async def _process_events(self, queue, count):  # pylint: disable=no-self-use
        object_counter = 0
        while object_counter < count:
            await queue.get()
            object_counter = object_counter + 1
            queue.task_done()
        await queue.join()

    @staticmethod
    def _notifications_response_object():
        return munch.Munch({
            'objects': [
                munch.Munch({'type': 'file', 'guid': 1, 'name': 'docs.txt', 'deleted': False})
            ],
            'more': False,
            'cursor': TestAsyncCoreNotifications._new_cursor
        })
