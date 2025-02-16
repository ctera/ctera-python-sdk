=========
Direct IO
=========

CTERA Direct IO is integrated into the CTERA Python SDK to enable high-speed, programmatic access to files within the CTERA Global Namespace. By leveraging CTERA Direct IO, applications can retrieve file metadata from the CTERA Portal while directly accessing data blocks from the underlying object storage, whether on-premises or in the cloud. This approach ensures efficient, concurrent, and secure retrieval, making it ideal for high-performance data pipelines.

The CTERA Python SDK provides two key extensions for CTERA Direct IO:

**Blocks API**: Enables concurrent retrieval of all blocks (chunks) that make up a file. It returns data payloads alongside metadata such as block offset and length, with no guaranteed order. This API is optimized for bulk data processing workflows.

**Streamer API**: Supports prioritized, sequential retrieval of file content, ensuring efficient access from the beginning to the end of a file. It also allows for byte-range retrieval by specifying start and end offsets, making it ideal for real-time streaming and partial file access scenarios.


Getting Started
===============

In this example, a file is downloaded using its unique ID (e.g., ``12345``) and written to disk as ``example.pdf``.
For more information on how to obtain the File ID, name, refer to the `Event <https://ctera-python-sdk.readthedocs.io/en/latest/api/cterasdk.asynchronous.core.types.html#cterasdk.asynchronous.core.types.Event>`_ object returned by the `Notification Service <https://ctera-python-sdk.readthedocs.io/en/latest/UserGuides/DataServices/NotificationService.html>`_.


.. code-block:: python

    import aiofiles
    from cterasdk import ctera_direct

    url = 'https://tenant.ctera.com'
    access_key_id = 'your-access-key-id'
    secret_access_key = 'your-secret-key'

    name = 'example.pdf'
    file_id = 12345  # unique identifier of a file

    async with aiofiles.open(name, 'wb') as f:
        async with ctera_direct.client.DirectIO(url, access_key_id, secret_access_key) as client:
            futures = await client.blocks(file_id)
            for future in asyncio.as_completed(futures):
                block = await future
                await f.seek(block.offset)
                await f.write(block.data)

..


SSL
---

During testing, you may need to disable SSL verification if the Portal or Object Storage certificate is not trusted by your host client.

.. code-block:: python

    import cterasdk.settings

    cterasdk.settings.sessions.ctera_direct.api.ssl = False  # disable CTERA Portal SSL verification
    cterasdk.settings.sessions.ctera_direct.storage.ssl = False  # disable Object Storage SSL verification


Blocks API
==========

.. automethod:: cterasdk.direct.client.Client.blocks
   :noindex:


Streamer API
============

.. automethod:: cterasdk.direct.client.Client.streamer
   :noindex:

.. code-block:: python

    import logging
    import asyncio

    import cterasdk.settings
    from cterasdk import ctera_direct


    logger = logging.getLogger('app')


    async def start_stream(file_id, offset):

        baseurl = 'https://tenant.ctera.com'
        access_key_id = 'your-access-key'
        secret_access_key = 'your-secret-key'

        async with ctera_direct.client.DirectIO(baseurl, access_key_id, secret_access_key) as client:
            streamer = await client.streamer(file_id, byte_range=ctera_direct.types.ByteRange(offset))

            logging.getLogger('app').info('Starting Stream. Offset: %s.', offset or 0)
            async for block in streamer.start():
                await handle_block(block)
            logging.getLogger('app').info('Ending Stream.')


    async def handle_block(block):
        logger.info('Playing video. Offset: %s, Size: %s.', block.offset, block.length)


    async def handle_error(error):
        logger.error('Streaming error for file: %s. Retrying in 5 seconds...', error.filename)
        await asyncio.sleep(5)


    async def stream(file_id, offset=None):
        success = False
        while not success:
            try:
                await start_stream(file_id, offset)
                success = True
            except ctera_direct.exceptions.StreamError as error:
                await handle_error(error)
                offset = error.offset  # Try to play from where stream was interrupted.


    if __name__ == '__main__':
        cterasdk.settings.sessions.ctera_direct.api.ssl = False
        cterasdk.settings.sessions.ctera_direct.storage.ssl = False

        file_id = 12345

        loop = asyncio.get_event_loop()
        loop.run_until_complete(stream(file_id))


Exceptions
==========

.. autoclass:: cterasdk.direct.exceptions.DirectIOError
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.direct.exceptions.DirectIOAPIError
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.direct.exceptions.BlockError
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.direct.exceptions.StreamError
   :noindex:
   :members:
   :show-inheritance:


Exceptions Hierarchy
--------------------

* IOError
    * DirectIOError
        * DirectIOAPIError
            * NotFoundError
            * UnAuthorized
            * UnprocessableContent
            * BlocksNotFoundError
            * BlockListConnectionError
            * BlockListTimeout
        * DecryptKeyError
        * BlockError
            * DownloadError
            * DownloadTimeout
            * DownloadConnectionError
            * DecryptBlockError
            * DecompressBlockError
            * BlockValidationException
        * StreamError