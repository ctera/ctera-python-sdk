import uuid
import munch

from cterasdk.core import activation
from tests.ut.core.admin import base_admin


class TestCoreActivation(base_admin.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._expected_code = str(uuid.uuid4())
        self._init_global_admin(get_response=munch.Munch(dict(code=self._expected_code)))
        self._username = 'admin'
        self._portal = 'portal'

    def test_generate_code_user_and_tenant(self):
        code = activation.Activation(self._global_admin).generate_code(self._username, self._portal)
        self._global_admin.api.get.assert_called_once_with('/ssoActivation', params=dict(username=self._username, portal=self._portal))
        self.assertEqual(code, self._expected_code)

    def test_generate_code_user_only(self):
        code = activation.Activation(self._global_admin).generate_code(self._username, None)
        self._global_admin.api.get.assert_called_once_with('/ssoActivation', params=dict(username=self._username))
        self.assertEqual(code, self._expected_code)
