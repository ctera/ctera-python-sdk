====================
Notification Service
====================

The Notification Service is a background service that subscribes to real-time file events and dispatches tasks to consumer threads.

It listens for file events and enqueues them in an ``asyncio.Queue`` queue.
Events are instances of the :py:class:`cterasdk.asynchronous.core.types.Event` class.
The queue blocks until all events have been processed.
Use the `task_done()` `function <https://docs.python.org/3/library/asyncio-queue.html#asyncio.Queue.task_done>`_ to indicate task completion.

After processing all events, the service executes a client-provided callback to record the latest cursor,
enabling the service to pause and resume from the last recorded position.

.. automethod:: cterasdk.asynchronous.core.notifications.Service.run
   :noindex:

.. code-block:: python

    import asyncio
    import logging
    from cterasdk import AsyncGlobalAdmin


    async def save_cursor(cursor):
        """Use this function to persist the cursor"""


    async def process_event(event):
        """Process an event"""


    async def worker(queue):
        """Sample worker thread"""
        while True:
            event = await queue.get()
            try:
                await process_event(event)
            except Exception:
                logging.getLogger().error('Error Message')
            finally:
                queue.task_done()  # Service will not produce events unless all tasks are done.


    async def main():
        cursor = None
        queue = asyncio.Queue()  # Shared queue between producer and consumer threads
        async with AsyncGlobalAdmin('tenant.ctera.com') as admin:
            await admin.login('admin-username', 'admin-password')
            """Start event producer service."""
            admin.notifications.service.run(queue, save_cursor, cursor=cursor)
            """Start event consumer to process events"""
            consumer = asyncio.create_task(worker(queue))
            await consumer
            await admin.logout()


    if __name__ == '__main__':
            asyncio.run(main())

..

Ancestors
---------

.. automethod:: cterasdk.asynchronous.core.notifications.Notifications.ancestors
   :noindex:

   List ancestors. Returns a sorted list comprised of the file event and all parent directory objects.

.. code-block:: python

    import asyncio
    import logging
    from pathlib import Path
    from cterasdk import AsyncGlobalAdmin
    import cterasdk.settings


    async def save_cursor(cursor):
        """Use this function to persist the cursor"""


    async def process_event(admin, event):  # Print full file path
        """Process an event"""
        ancestors = await admin.notifications.ancestors(event)
        print(Path(*[ancestor.name for ancestor in ancestors]).as_posix())


    async def worker(admin, queue):
        """Sample worker thread"""
        while True:
            event = await queue.get()
            try:
                if event.type == 'file' and not event.deleted:  # if file exists
                    await process_event(admin, event)
            except Exception:
                logging.getLogger().error('Error Message')
            finally:
                queue.task_done()  # Service will not produce events unless all tasks are done.


    async def main():
        cterasdk.settings.sessions.metadata_connector.ssl = False
        cursor = None
        queue = asyncio.Queue()  # Shared queue between producer and consumer threads
        async with AsyncGlobalAdmin('tenant.ctera.com') as admin:
            await admin.login('admin-username', 'admin-password')
            """Start event producer service."""
            admin.notifications.service.run(queue, save_cursor, cursor=cursor)
            """Start event consumer to process events"""
            consumer = asyncio.create_task(worker(admin, queue))
            await consumer
            await admin.logout()


    if __name__ == '__main__':
            asyncio.run(main())

..


Code Snippets
-------------

.. code-block:: python

    import aiofiles
    import asyncio
    from cterasdk import AsyncGlobalAdmin, ctera_direct
    import cterasdk.settings


    async def save_cursor(cursor):
        """Use this function to persist the cursor"""

    def acquire_client():
        url = 'https://tenant.ctera.com'
        access_key_id = 'your-access-key-id'
        secret_access_key = 'your-secret-key''
        return ctera_direct.client.DirectIO(url, access_key_id, secret_access_key)


    async def download_file(file_id, name):  # download files to local directory
        async with aiofiles.open(name, 'wb') as f:
            async with acquire_client() as client:
                futures = await client.blocks(file_id)
                for future in asyncio.as_completed(futures):
                    block = await future
                    await f.seek(block.offset)
                    await f.write(block.data)


    async def worker(queue):
        while True:
            event = await queue.get()
            try:
                if event.type == 'file' and not event.deleted:  # download all files if not deleted
                    await download_file(event.id, event.name)
            except Exception as e:
                print(e)
            finally:
                queue.task_done()  # Service will not produce events unless all tasks are done.


    async def main():
        cterasdk.settings.sessions.metadata_connector.ssl = False
        cterasdk.settings.sessions.ctera_direct.api.ssl = False
        cursor = None
        queue = asyncio.Queue()  # Shared queue between producer and consumer threads
        async with AsyncGlobalAdmin('tenant.ctera.com') as admin:
            await admin.login('admin-username', 'admin-password')
            """Start event producer service."""
            admin.notifications.service.run(queue, save_cursor, cursor=cursor)
            """Start event consumer to process events"""
            consumer = asyncio.create_task(worker(queue))
            await consumer
            await admin.logout()


    if __name__ == '__main__':
            asyncio.run(main())

..
