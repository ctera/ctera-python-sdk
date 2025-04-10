from unittest import mock
import munch
from cterasdk.asynchronous.core import notifications
from cterasdk.core.types import CloudFSFolderFindingHelper, UserAccount
from cterasdk import exceptions
from tests.ut.aio import base_core


class TestAsyncCoreNotifications(base_core.BaseAsyncCoreTest):

    def setUp(self):
        super().setUp()
        self._cursor = 'abcd'
        self._cloudfolder_ids = [1, 2, 3, 4]
        self._cloudfolder_id = 56789
        self._cloudfolders = [
            CloudFSFolderFindingHelper('My Files', UserAccount('jsmith'))
        ]
        self._descendant = munch.Munch({
            'folder_id': self._cloudfolder_id,
            'guid': 'abcd'
        })

    async def test_get_notifications_defaults(self):
        has_more = False
        self._init_global_admin(post_response=TestAsyncCoreNotifications._create_cursor_response(has_more, self._cursor, []))
        ret = await notifications.Notifications(self._global_admin).get()
        self._global_admin.v2.api.post.assert_called_once_with('/metadata/list', mock.ANY)
        expected_param = TestAsyncCoreNotifications._create_parameter(max_results=2000)
        actual_param = self._global_admin.v2.api.post.call_args[0][1]
        self.assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret.objects, [])
        self.assertEqual(ret.cursor, self._cursor)
        self.assertEqual(ret.more, has_more)

    async def test_get_notifications_error(self):
        self._init_global_admin(post_response=None)
        with self.assertRaises(exceptions.NotificationsError) as error:
            await notifications.Notifications(self._global_admin).get()
        self._global_admin.v2.api.post.assert_called_once_with('/metadata/list', mock.ANY)
        self.assertEqual(error.exception.cloudfolders, None)
        self.assertEqual(error.exception.cursor, None)

    async def test_get_notifications_cursor_max_results(self):
        self._init_global_admin(post_response=TestAsyncCoreNotifications._create_cursor_response(False, self._cursor, []))
        await notifications.Notifications(self._global_admin).get(cursor=self._cursor, max_results=5)
        self._global_admin.v2.api.post.assert_called_once_with('/metadata/list', mock.ANY)
        expected_param = TestAsyncCoreNotifications._create_parameter(cursor=self._cursor, max_results=5)
        actual_param = self._global_admin.v2.api.post.call_args[0][1]
        self.assert_equal_objects(actual_param, expected_param)

    async def test_get_notifications_cloudfolder_ids(self):
        self._init_global_admin(post_response=TestAsyncCoreNotifications._create_cursor_response(False, self._cursor, []))
        await notifications.Notifications(self._global_admin).get(cloudfolders=self._cloudfolder_ids)
        self._global_admin.v2.api.post.assert_called_once_with('/metadata/list', mock.ANY)
        expected_param = TestAsyncCoreNotifications._create_parameter(folder_ids=self._cloudfolder_ids, max_results=2000)
        actual_param = self._global_admin.v2.api.post.call_args[0][1]
        self.assert_equal_objects(actual_param, expected_param)

    async def test_get_notifications_cloudfolders_finder(self):
        self._init_global_admin(post_response=TestAsyncCoreNotifications._create_cursor_response(False, self._cursor, []))
        self._global_admin.cloudfs.drives.find = mock.AsyncMock()

        cloudfolders = [munch.Munch({'uid': self._cloudfolder_id})]

        async def generator():
            for cloudfolder in cloudfolders:
                yield cloudfolder

        self._global_admin.cloudfs.drives.find = mock.AsyncMock(return_value=generator())
        await notifications.Notifications(self._global_admin).get(cloudfolders=self._cloudfolders)
        expected_param = TestAsyncCoreNotifications._create_parameter(folder_ids=[self._cloudfolder_id], max_results=2000)
        actual_param = self._global_admin.v2.api.post.call_args[0][1]
        self.assert_equal_objects(actual_param, expected_param)

    async def test_changes_defaults_no_changes(self):
        self._init_global_admin(post_response=TestAsyncCoreNotifications._create_changes_response(False))
        await notifications.Notifications(self._global_admin).changes(self._cursor)
        self._global_admin.v2.api.post.assert_called_once_with('/metadata/longpoll', mock.ANY)
        expected_param = TestAsyncCoreNotifications._create_parameter(cursor=self._cursor, timeout=10000)
        actual_param = self._global_admin.v2.api.post.call_args[0][1]
        self.assert_equal_objects(actual_param, expected_param)

    async def test_ancestors_success(self):
        post_response = 'Success'
        self._init_global_admin(post_response=post_response)
        ret = await notifications.Notifications(self._global_admin).ancestors(self._descendant)
        self._global_admin.v2.api.post.assert_called_once_with('/metadata/ancestors', mock.ANY)
        expected_param = munch.Munch({
            'folder_id': self._descendant.folder_id,
            'guid': self._descendant.guid,
        })
        actual_param = self._global_admin.v2.api.post.call_args[0][1]
        self.assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, post_response)

    async def test_ancestors_error(self):
        self._init_global_admin()
        self._global_admin.v2.api.post = mock.AsyncMock(side_effect=exceptions.ClientResponseException(munch.Munch({})))
        with self.assertRaises(exceptions.ClientResponseException) as error:
            await notifications.Notifications(self._global_admin).ancestors(self._descendant)
        self.assertEqual(error.exception.message, 'An error occurred while processing the HTTP request.')

    @staticmethod
    def _create_parameter(folder_ids=None, cursor=None, max_results=None, timeout=None):
        param = munch.Munch({
            'folder_ids': folder_ids if folder_ids else [],
            'cursor': cursor
        })
        if max_results:
            param.max_results = max_results
        if timeout:
            param.timeout = timeout
        return param

    @staticmethod
    def _create_cursor_response(has_more, cursor, entries=None):
        return munch.Munch({
            'has_more': has_more,
            'cursor': cursor,
            'entries': entries if entries else []
        })

    @staticmethod
    def _create_changes_response(changes):
        return munch.Munch({
            'changes': changes
        })
