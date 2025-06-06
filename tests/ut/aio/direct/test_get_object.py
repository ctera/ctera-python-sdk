import asyncio
from http import HTTPStatus
import errno
from unittest import mock
import munch
from cterasdk.direct.lib import get_object
from cterasdk import exceptions, ctera_direct
from . import base


class BaseDirectMetadata(base.BaseAsyncDirect):

    def setUp(self):  # pylint: disable=arguments-differ
        super().setUp()
        self._retries = 3
        self._file_id = 12345

    async def test_get_object_connection_error(self):
        chunk = BaseDirectMetadata._create_chunk()
        self._direct._client._client.get.side_effect = ConnectionError  # pylint: disable=protected-access
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(exceptions.direct.DownloadConnectionError) as error:
                await get_object(self._direct._client._client, self._file_id, chunk)  # pylint: disable=protected-access
        self.assertEqual(error.exception.errno, errno.ENETRESET)
        self.assertEqual(error.exception.strerror, 'Failed to download block. Connection error')
        self.assertEqual(error.exception.filename, self._file_id)
        self.assert_equal_objects(error.exception.block, BaseDirectMetadata._create_block_info(self._file_id, chunk))

    async def test_get_object_timeout(self):
        chunk = BaseDirectMetadata._create_chunk()
        self._direct._client._client.get.side_effect = asyncio.TimeoutError  # pylint: disable=protected-access
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(exceptions.direct.DownloadTimeout) as error:
                await get_object(self._direct._client._client, self._file_id, chunk)  # pylint: disable=protected-access
        self.assertEqual(error.exception.errno, errno.ETIMEDOUT)
        self.assertEqual(error.exception.strerror, 'Failed to download block. Timed out')
        self.assertEqual(error.exception.filename, self._file_id)
        self.assert_equal_objects(error.exception.block, BaseDirectMetadata._create_block_info(self._file_id, chunk))

    async def test_response_read_io_error(self):
        message = 'Error reading block.'
        chunk = BaseDirectMetadata._create_chunk()

        async def stream_reader():
            raise IOError(message)

        self._direct._client._client.get.return_value = munch.Munch({'read': stream_reader})  # pylint: disable=protected-access
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(exceptions.direct.DownloadError) as error:
                await get_object(self._direct._client._client, self._file_id, chunk)  # pylint: disable=protected-access
        self.assertEqual(error.exception.errno, errno.EIO)
        self.assertEqual(str(error.exception.strerror), message)
        self.assertEqual(error.exception.filename, self._file_id)
        self.assert_equal_objects(error.exception.block, BaseDirectMetadata._create_block_info(self._file_id, chunk))

    async def test_get_client_error(self):
        chunk = BaseDirectMetadata._create_chunk()
        self._direct._client._client.get.side_effect = exceptions.transport.HTTPError(  # pylint: disable=protected-access
            HTTPStatus.INTERNAL_SERVER_ERROR,
            BaseDirectMetadata._create_error_object(HTTPStatus.INTERNAL_SERVER_ERROR.value)
        )
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(exceptions.direct.DownloadError) as error:
                await get_object(self._direct._client._client, self._file_id, chunk)  # pylint: disable=protected-access
        self.assertEqual(error.exception.errno, errno.EIO)
        self.assertEqual(error.exception.strerror.response.status, 500)
        self.assertEqual(error.exception.filename, self._file_id)
        self.assert_equal_objects(error.exception.block, BaseDirectMetadata._create_block_info(self._file_id, chunk))

    @staticmethod
    def _create_error_object(status):
        return munch.Munch(
            dict(
                request=munch.Munch(dict(url='/xyz')),
                response=munch.Munch(dict(status=status))
            )
        )

    @staticmethod
    def _create_block_info(file_id, chunk):
        return munch.Munch({
            'file_id': file_id,
            'number': chunk.index,
            'offset': chunk.offset,
            'length': chunk.length
        })

    @staticmethod
    def _create_chunk():
        return munch.Munch({
            'url': 'https://s3.amazonaws.com/test',
            'index': 1,
            'offset': 0,
            'length': 4096
        })
