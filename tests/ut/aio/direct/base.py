from unittest import mock
from cterasdk import ctera_direct
from .. import base


class BaseAsyncDirect(base.BaseAsyncTest):

    def setUp(self, access=None, secret=None):
        super().setUp()
        self._direct = ctera_direct.client.DirectIO('', access, secret)
        self._direct._client._api.get = mock.AsyncMock()  # pylint: disable=protected-access
        self._direct._client._client.get = mock.AsyncMock()  # pylint: disable=protected-access
        self._authorization_header = {'Authorization': f'Bearer {access}'}
