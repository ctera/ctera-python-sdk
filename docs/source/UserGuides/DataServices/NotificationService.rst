====================
Notification Service
====================

This library includes a background service designed for subscribing to real-time file events
and dispatching tasks to consumer threads.

The service subscribes to file events and enqueues them to an ``asyncio.Queue`` queue.
Events are instances of the :py:class:`cterasdk.asynchronous.core.types.Event` class.
The queue blocks until all events were consumed and processed.
Use the `task_done()` `function <https://docs.python.org/3/library/asyncio-queue.html#asyncio.Queue.task_done>`_ to signal that formerly enqueued task is complete.

After processing all events, the service will perform a callback to a function provided by the client to record the latest cursor.
Recording the cursor enables pausing and resuming the service from the last cursor position.

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


    async def save_cursor(cursor):
        """Use this function to persist the cursor"""


    async def process_event(admin, event):
        """Process an event"""
        ancestors = await admin.metadata.ancestors(event)
        print(Path(*[ancestor.name for ancestor in ancestors]).as_posix())


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
