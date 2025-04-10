import asyncio
import errno
from unittest import mock
import munch
from cterasdk import ctera_direct
from cterasdk import exceptions, Object
from . import base


class BaseDirectMetadata(base.BaseAsyncDirect):

    def setUp(self):  # pylint: disable=arguments-differ
        super().setUp()
        self._retries = 3
        self._file_id = 12345

    async def test_retries_on_error(self):
        self._direct._client._api.get.return_value = munch.Munch({'chunks': None})  # pylint: disable=protected-access
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(ctera_direct.exceptions.BlocksNotFoundError):
                await self._direct.metadata(self._file_id)
        self._direct._client._api.get.assert_has_calls(  # pylint: disable=protected-access
            self._retries * [
                mock.call(f'{self._file_id}', headers=self._authorization_header),
            ]
        )

    async def test_get_file_metadata_not_found(self):
        self._direct._client._api.get.return_value = munch.Munch({'chunks': None})  # pylint: disable=protected-access
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(ctera_direct.exceptions.BlocksNotFoundError) as error:
                await self._direct.metadata(self._file_id)
        self.assertEqual(error.exception.errno, errno.ENODATA)
        self.assertEqual(error.exception.strerror, 'Blocks not found')
        self.assertEqual(error.exception.filename, self._file_id)

    async def test_get_file_metadata_error_400(self):
        self._direct._client._api.get.side_effect = exceptions.ClientResponseException(  # pylint: disable=protected-access
            BaseDirectMetadata._create_error_object(400)
        )
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(ctera_direct.exceptions.NotFoundError) as error:
                await self._direct.metadata(self._file_id)
        self.assertEqual(error.exception.errno, errno.EBADF)
        self.assertEqual(error.exception.strerror, 'File not found')
        self.assertEqual(error.exception.filename, self._file_id)

    async def test_get_file_metadata_error_401(self):
        self._direct._client._api.get.side_effect = exceptions.ClientResponseException(  # pylint: disable=protected-access
            BaseDirectMetadata._create_error_object(401)
        )
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(ctera_direct.exceptions.UnAuthorized) as error:
                await self._direct.metadata(self._file_id)
        self.assertEqual(error.exception.errno, errno.EACCES)
        self.assertEqual(error.exception.strerror, 'Unauthorized: You do not have the necessary permissions to access this resource')
        self.assertEqual(error.exception.filename, self._file_id)

    async def test_get_file_metadata_error_422(self):
        self._direct._client._api.get.side_effect = exceptions.ClientResponseException(  # pylint: disable=protected-access
            BaseDirectMetadata._create_error_object(422)
        )
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(ctera_direct.exceptions.UnprocessableContent) as error:
                await self._direct.metadata(self._file_id)
        self.assertEqual(error.exception.errno, errno.ENOTSUP)
        self.assertEqual(error.exception.strerror, 'Not all blocks of the requested file are stored on a storage node set to Direct Mode')
        self.assertEqual(error.exception.filename, self._file_id)

    async def test_get_file_metadata_unknown_error(self):
        self._direct._client._api.get.side_effect = exceptions.ClientResponseException(  # pylint: disable=protected-access
            BaseDirectMetadata._create_error_object(500)
        )
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(exceptions.ClientResponseException) as error:
                await self._direct.metadata(self._file_id)
        self.assertEqual(error.exception.message, 'An error occurred while processing the HTTP request.')

    async def test_get_file_metadata_connection_error(self):
        self._direct._client._api.get.side_effect = ConnectionError  # pylint: disable=protected-access
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(ctera_direct.exceptions.BlockListConnectionError) as error:
                await self._direct.metadata(self._file_id)
        self.assertEqual(error.exception.errno, errno.ENETRESET)
        self.assertEqual(error.exception.strerror, 'Failed to list blocks. Connection error')
        self.assertEqual(error.exception.filename, self._file_id)

    async def test_get_file_metadata_timeout(self):
        self._direct._client._api.get.side_effect = asyncio.TimeoutError  # pylint: disable=protected-access
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(ctera_direct.exceptions.BlockListTimeout) as error:
                await self._direct.metadata(self._file_id)
        self.assertEqual(error.exception.errno, errno.ETIMEDOUT)
        self.assertEqual(error.exception.strerror, 'Failed to list blocks. Timed out')
        self.assertEqual(error.exception.filename, self._file_id)

    @staticmethod
    def _create_error_object(status):
        param = Object()
        param.response = Object()
        param.response.status = status
        return param
