import errno
import munch
import asyncio
from unittest import mock
from cterasdk.direct.lib import get_object
from cterasdk import exceptions, ctera_direct, Object
from . import base


class BaseDirectMetadata(base.BaseAsyncDirect):

    def setUp(self):
        super().setUp()
        self._retries = 3
        self._file_id = 12345

    async def test_get_object_connection_error(self):
        chunk = BaseDirectMetadata._create_chunk()
        self._direct._client._client.get.side_effect = ConnectionError
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(ctera_direct.exceptions.DownloadConnectionError) as error:
                await get_object(self._direct._client._client, self._file_id, chunk)
        self.assertEqual(error.exception.errno, errno.ENETRESET)
        self.assertEqual(error.exception.strerror, 'Failed to download block. Connection error')
        self.assertEqual(error.exception.filename, self._file_id)
        self.assert_equal_objects(error.exception.block, BaseDirectMetadata._create_block_info(self._file_id, chunk))

    async def test_get_object_timeout(self):
        chunk = BaseDirectMetadata._create_chunk()
        self._direct._client._client.get.side_effect = asyncio.TimeoutError
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(ctera_direct.exceptions.DownloadTimeout) as error:
                await get_object(self._direct._client._client, self._file_id, chunk)
        self.assertEqual(error.exception.errno, errno.ETIMEDOUT)
        self.assertEqual(error.exception.strerror, 'Failed to download block. Timed out')
        self.assertEqual(error.exception.filename, self._file_id)
        self.assert_equal_objects(error.exception.block, BaseDirectMetadata._create_block_info(self._file_id, chunk))

    async def test_response_read_io_error(self):
        message = 'Error reading block.'
        chunk = BaseDirectMetadata._create_chunk()
        async def stream_reader():
            raise IOError(message)
        self._direct._client._client.get.return_value = munch.Munch({'read': stream_reader})
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(ctera_direct.exceptions.DownloadError) as error:
                await get_object(self._direct._client._client, self._file_id, chunk)
        self.assertEqual(error.exception.errno, errno.EIO)
        self.assertEqual(str(error.exception.strerror), message)
        self.assertEqual(error.exception.filename, self._file_id)
        self.assert_equal_objects(error.exception.block, BaseDirectMetadata._create_block_info(self._file_id, chunk))

    async def test_get_client_error(self):
        chunk = BaseDirectMetadata._create_chunk()
        self._direct._client._client.get.side_effect = exceptions.ClientResponseException(self._create_error_object(500))
        with mock.patch('asyncio.sleep'):
            with self.assertRaises(ctera_direct.exceptions.DownloadError) as error:
                await get_object(self._direct._client._client, self._file_id, chunk)
        self.assertEqual(error.exception.errno, errno.EIO)
        self.assertEqual(error.exception.strerror.status, 500)
        self.assertEqual(error.exception.filename, self._file_id)
        self.assert_equal_objects(error.exception.block, BaseDirectMetadata._create_block_info(self._file_id, chunk))

    @staticmethod
    def _create_error_object(status):
        param = Object()
        param.response = Object()
        param.response.status = status
        return param

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
