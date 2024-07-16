import asyncio
import logging


class Streamer:

    def __init__(self, promises, counter=1):
        self._promises = promises
        self._queue = asyncio.Queue()
        self._counter = counter
        self._blocks = dict()
        self._streamer = asyncio.create_task(self._stream())

    def __aiter__(self):
        return self

    async def _stream(self):
        message = {'count': len(self._promises)}
        logging.getLogger('cterasdk.direct').debug('Gathering Blocks. %s', message)
        for promise in asyncio.as_completed(self._promises):
            logging.getLogger('cterasdk.direct').debug('Put Block.')
            await self._queue.put(await promise)
        logging.getLogger('cterasdk.direct').debug('Completed Gathering Blocks. %s', message)

    async def __anext__(self):
        if self._counter > len(self._promises):
            raise StopAsyncIteration

        while self._blocks.get(self._counter, None) is None:
            try:
                block = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                self._blocks[block.number] = block
            except asyncio.TimeoutError:
                logging.getLogger('cterasdk.direct').debug('Timeout.')

        block = self._blocks.pop(self._counter)
        self._counter = self._counter + 1
        return block.data
