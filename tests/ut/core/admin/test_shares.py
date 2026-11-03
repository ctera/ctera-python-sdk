from unittest import mock

import munch

from cterasdk import exceptions
from cterasdk.core import shares
from cterasdk.core.types import Share
from tests.ut.core.admin import base_admin


class TestCoreShares(base_admin.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._share_id = '05db1713-842e-4f7b-ac27-43787f10c695'
        self._configuration = munch.Munch({
            'id': self._share_id,
            'directory': '/cloud/users/Admin user/Projects',
            'access_type': 'winAclMode',
            'device_shares': [munch.Munch({'device_name': 'edge1'})],
            'acl_rules': [],
        })

    def test_get_configuration(self):
        self._mock_configuration(self._configuration)
        ret = shares.Shares(self._global_admin).get_configuration(self._share_id)
        self._global_admin.clients.v2.get.assert_called_once_with(f'shareManagement/configurations/{self._share_id}')
        self.assertEqual(ret.directory, '/cloud/users/Admin user/Projects')
        self.assertEqual(ret.access_type, 'winAclMode')
        self.assertEqual(ret.device_shares[0].device_name, 'edge1')

    def test_get_configuration_from_share(self):
        self._mock_configuration(self._configuration)
        share = Share(self._share_id, 'Projects', 'Admin user/Projects', ['SMB'], 'winAclMode', ['edge1'])
        ret = shares.Shares(self._global_admin).get_configuration(share)
        self._global_admin.clients.v2.get.assert_called_once_with(f'shareManagement/configurations/{self._share_id}')
        self.assertEqual(ret, self._configuration)

    def test_get_configuration_not_found(self):
        self._mock_configuration(None)
        with self.assertRaises(exceptions.ObjectNotFoundException) as error:
            shares.Shares(self._global_admin).get_configuration(self._share_id)
        self.assertEqual(f'Object not found: {self._share_id}', str(error.exception))

    def _mock_configuration(self, configuration):
        response = None if configuration is None else munch.Munch({'data': configuration})
        self._global_admin.clients.v2.get = mock.MagicMock(return_value=response)
