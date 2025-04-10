from unittest import mock
import munch
from cterasdk.asynchronous.core import users
from cterasdk.core.types import UserAccount
from cterasdk import exceptions
from tests.ut.aio import base_core


class TestAsyncCoreUsers(base_core.BaseAsyncCoreTest):

    def setUp(self):
        super().setUp()
        self._username = 'jsmith'
        self._domain = 'ctera.com'
        self._local_user = UserAccount(self._username)
        self._domain_user = UserAccount(self._username, self._domain)

    async def test_get_local_user(self):
        self._init_global_admin(get_multi_response=TestAsyncCoreUsers._user_object(**{'name': self._username}))
        ret = await users.Users(self._global_admin).get(self._local_user)
        self._global_admin.v1.api.get_multi.assert_called_once_with(f'/users/{self._username}', mock.ANY)
        for att in users.Users.default:
            self.assertIn(f'/{att}', self._global_admin.v1.api.get_multi.call_args[0][1])
        self.assertEqual(ret.name, self._username)

    async def test_get_domain_user(self):
        self._init_global_admin(get_multi_response=TestAsyncCoreUsers._user_object(**{'name': self._username, 'domain': self._domain}))
        ret = await users.Users(self._global_admin).get(self._domain_user)
        self._global_admin.v1.api.get_multi.assert_called_once_with(f'/domains/{self._domain}/adUsers/{self._username}', mock.ANY)
        for att in users.Users.default:
            self.assertIn(f'/{att}', self._global_admin.v1.api.get_multi.call_args[0][1])
        self.assertEqual(ret.name, self._username)
        self.assertEqual(ret.domain, self._domain)

    async def test_user_not_found(self):
        self._init_global_admin(get_multi_response=TestAsyncCoreUsers._user_object(**{'name': None}))
        with self.assertRaises(exceptions.ObjectNotFoundException) as error:
            await users.Users(self._global_admin).get(self._local_user)
        self.assertEqual(error.exception.message, 'Could not find user')

    @staticmethod
    def _user_object(**kwargs):
        return munch.Munch(**kwargs)
