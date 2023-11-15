# pylint: disable=protected-access
import munch

from cterasdk.core.types import UserAccount
from cterasdk.core import credentials
from tests.ut import base_core


class TestCoreCredentialsS3(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._user_account = UserAccount('user')
        self._uid = 1500
        self._access_key_id = 'ABCD'
        self._access_key_uid = 2500
        self._mock_get_user_uid = self.patch_call("cterasdk.core.users.Users.get")
        self._mock_get_user_uid.return_value = munch.Munch({'uid': self._uid})

    def test_list_s3_credentials(self):
        execute_response = 'Success'
        self._init_global_admin(execute_response=execute_response)
        ret = credentials.S3(self._global_admin).all(self._user_account)
        self._mock_get_user_uid.assert_called_once_with(self._user_account, ['uid'])
        self._global_admin.execute.assert_called_once_with('', 'getApiKeys', self._uid)
        self.assertEqual(ret, execute_response)

    def test_create_s3_credential(self):
        execute_response = 'Success'
        self._init_global_admin(execute_response=execute_response)
        ret = credentials.S3(self._global_admin).create(self._user_account)
        self._mock_get_user_uid.assert_called_once_with(self._user_account, ['uid'])
        self._global_admin.execute.assert_called_once_with('', 'createApiKey', self._uid)
        self.assertEqual(ret, execute_response)

    def test_delete_s3_credential_success(self):
        execute_response = 'Success'
        mock_get_s3_credentials = self.patch_call("cterasdk.core.credentials.S3.all")
        mock_get_s3_credentials.return_value = [munch.Munch({'accessKey': self._access_key_id, 'uid': self._access_key_uid})]
        self._init_global_admin(execute_response=execute_response)
        ret = credentials.S3(self._global_admin).delete(self._access_key_id, self._user_account)
        mock_get_s3_credentials.assert_called_once_with(self._user_account)
        self._global_admin.execute.assert_called_once_with('', 'deleteApiKey', self._access_key_uid)
        self.assertEqual(ret, execute_response)

    def test_delete_s3_credential_not_found(self):
        self._init_global_admin()
        mock_get_s3_credentials = self.patch_call("cterasdk.core.credentials.S3.all")
        mock_get_s3_credentials.return_value = [munch.Munch({'accessKey': self._access_key_id, 'uid': self._access_key_uid})]
        ret = credentials.S3(self._global_admin).delete('not_found', self._user_account)
        mock_get_s3_credentials.assert_called_once_with(self._user_account)
        self._global_admin.execute.assert_not_called()
        self.assertEqual(ret, None)
