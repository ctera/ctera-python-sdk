import asyncio
import errno
from http import HTTPStatus
from unittest import mock
import munch
from cterasdk import ctera_direct
from cterasdk import exceptions
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
        self.assertEqual(error.exception.strerror, f'Could not find blocks for file ID: {self._file_id}')
        self.assertEqual(error.exception.filename, self._file_id)

    async def test_get_file_metadata_error_400(self):
        self._direct._client._api.get.side_effect = exceptions.HTTPError(  # pylint: disable=protected-access
            HTTPStatus.BAD_REQUEST,
            BaseDirectMetadata._create_error_object()
        )
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(ctera_direct.exceptions.NotFoundError) as error:
                await self._direct.metadata(self._file_id)
        self.assertEqual(error.exception.errno, errno.EBADF)
        self.assertEqual(error.exception.strerror, 'File not found')
        self.assertEqual(error.exception.filename, self._file_id)

    async def test_get_file_metadata_error_401(self):
        self._direct._client._api.get.side_effect = exceptions.HTTPError(  # pylint: disable=protected-access
            HTTPStatus.UNAUTHORIZED,
            BaseDirectMetadata._create_error_object()
        )
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(ctera_direct.exceptions.UnAuthorized) as error:
                await self._direct.metadata(self._file_id)
        self.assertEqual(error.exception.errno, errno.EACCES)
        self.assertEqual(error.exception.strerror, 'Unauthorized: You do not have the necessary permissions to access this resource')
        self.assertEqual(error.exception.filename, self._file_id)

    async def test_get_file_metadata_error_422(self):
        self._direct._client._api.get.side_effect = exceptions.HTTPError(  # pylint: disable=protected-access
            HTTPStatus.UNPROCESSABLE_ENTITY,
            BaseDirectMetadata._create_error_object()
        )
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(ctera_direct.exceptions.UnprocessableContent) as error:
                await self._direct.metadata(self._file_id)
        self.assertEqual(error.exception.errno, errno.ENOTSUP)
        self.assertEqual(error.exception.strerror, 'Not all blocks of the requested file are stored on a storage node set to Direct Mode')
        self.assertEqual(error.exception.filename, self._file_id)

    async def test_get_file_metadata_unknown_error(self):
        url = '/xyz'
        self._direct._client._api.get.side_effect = exceptions.HTTPError(  # pylint: disable=protected-access
            HTTPStatus.INTERNAL_SERVER_ERROR,
            BaseDirectMetadata._create_error_object()
        )
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(exceptions.HTTPError) as error:
                await self._direct.metadata(self._file_id)
        self.assertEqual(error.exception.error.request.url, url)

    async def test_get_file_metadata_connection_error(self):
        self._direct._client._api.get.side_effect = ConnectionError  # pylint: disable=protected-access
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(ctera_direct.exceptions.BlockListConnectionError) as error:
                await self._direct.metadata(self._file_id)
        self.assertEqual(error.exception.errno, errno.ENETRESET)
        self.assertEqual(error.exception.strerror,
                         f'Failed to list blocks for file ID: {self._file_id} due to a connection error')
        self.assertEqual(error.exception.filename, self._file_id)

    async def test_get_file_metadata_timeout(self):
        self._direct._client._api.get.side_effect = asyncio.TimeoutError  # pylint: disable=protected-access
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(ctera_direct.exceptions.BlockListTimeout) as error:
                await self._direct.metadata(self._file_id)
        self.assertEqual(error.exception.errno, errno.ETIMEDOUT)
        self.assertEqual(error.exception.strerror,
                         f'Timed out while listing blocks for file ID: {self._file_id}')
        self.assertEqual(error.exception.filename, self._file_id)

    @staticmethod
    def _create_error_object():
        return munch.Munch(
            dict(request=munch.Munch(
                dict(url='/xyz')
            ))
        )