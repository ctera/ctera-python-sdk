==================
Metadata Connector
==================


The CTERA Metadata Connector serves as a Change Notification Service for the CTERA Global File System,
providing real-time updates on file operations. CTERA Portal aggregates file events captured across a distributed environment
and presents API endpoints for subscribing to receive these events.

The Metadata Connector features API endpoints for retrieving file events, long polling to wait for changes, and retrieving a
list of ancestors (parent directories) for a given event.

For parallel processing of events, the CTERA SDK for Python features an asynchronous implementation of the Metadata Connector APIs.

.. automethod:: cterasdk.asynchronous.core.metadata.Metadata.get
   :noindex:

   Retrieve events from one or more Cloud Drive Folders. Returns an asynchronous iterator of file events.
   Additionally, the iterator includes an opaque `cursor` property clients can use to advance through the list of events.

.. code-block:: python

    import asyncio
    from cterasdk import DataServices, core_types

    async def main():
        async with DataServices('tenant.ctera.com') as admin:
            await admin.login('admin-username', 'admin-password')

            """Subscribing to all Cloud Drive Folders"""
            events = await admin.metadata.get()
            async for event in events:
                print(event)
            cursor = events.cursor  # Save cursor to advance through the list of events.

            """Get Changes from Cursor"""
            events = await admin.metadata.get(cursor=cursor)  # Get updates occuring after the cursor.
            async for event in events:
                print(event)

            """Subscribe to Specific Cloud Drive Folders"""
            drives = [
                core_types.CloudFSFolderFindingHelper('Documents', core_types.UserAccount('jsmith')),  # Local User
                core_types.CloudFSFolderFindingHelper('Documents', core_types.UserAccount('slee', 'acme.com')),  # Domain User
            ]
            events = await admin.metadata.get(drives=drives)
            async for event in events:
                print(event)
            cursor = events.cursor

            await admin.logout()

    if __name__ == '__main__':
        asyncio.run(main())

..

.. automethod:: cterasdk.asynchronous.core.metadata.Metadata.changes
   :noindex:

   Wait for changes.

.. code-block:: python

    import asyncio
    from cterasdk import DataServices

    async def main():
        cursor = None
        async with DataServices('tenant.ctera.com') as admin:
            await admin.login('admin-username', 'admin-password')
            while True:
                if await admin.metadata.changes(cursor)
                    events = await admin.metadata.get(cursor=cursor)
                    async for event in events:
                        print(event)
                    cursor = events.cursor
            await admin.logout()

    if __name__ == '__main__':
        asyncio.run(main())

..

.. automethod:: cterasdk.asynchronous.core.metadata.Metadata.ancestors
   :noindex:

   List ancestors. Returns a sorted list comprised of the file event and all parent directory objects.
   Use this API endpoint to comprise a full file or folder path.

.. code-block:: python

    import asyncio
    import pathlib
    from cterasdk import DataServices

    async def main():
        cursor = None
        async with DataServices('tenant.ctera.com') as admin:
            await admin.login('admin-username', 'admin-password')
            while True:
                if await admin.metadata.changes(cursor)
                    events = await admin.metadata.get(cursor=cursor)
                    async for event in events:
                        ancestors = await admin.metadata.ancestors(event)
                        path = pathlib.Path(*[ancestor.name for ancestor in ancestors])
                        print(path.as_posix())
                    cursor = events.cursor
            await admin.logout()

    if __name__ == '__main__':
        asyncio.run(main())

..

Metadata Service
----------------

Alternatively, this library includes a background service designed for subscribing to real-time file events
and dispatching tasks to consumer threads.
The service effectively subscribes to file events and enqueues them to an ``asyncio.Queue`` queue.
All enqueued file events are represeted as :py:class:`cterasdk.common.object.Object` object.
It blocks active until all events are consumed and the **task_done()** was called to signal.
After processing all events, the service triggers a callback function supplied by the client to store the cursor.
Recording the cursor enables pausing and resuming the service from the last cursor position.

.. automethod:: cterasdk.asynchronous.core.metadata.Service.run
   :noindex:

.. code-block:: python

    import asyncio
    import logging
    from cterasdk import DataServices


    async def save_cursor(cursor):
        """Use this function to persist the cursor"""


    async def process_event(event)
        """Process an event"""


    async def consumer(queue):
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
        async with DataServices('tenant.ctera.com') as admin:
            await admin.login('admin-username', 'admin-password')
            """Start the event producer service."""
            producer = admin.metadata.service.run(queue, save_cursor, cursor=cursor)
            """Start 10 consumers to process events"""
            consumers = [asyncio.create_task(consumer(queue)) for i in range(0, 10)]
            await producer
            await asyncio.gather(consumers)
            await admin.logout()

    if __name__ == '__main__':
        asyncio.run(main())

..
