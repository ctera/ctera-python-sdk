import logging

from abc import abstractmethod


class BaseAsyncIterator:
    """Abstract Asynchronous Iterator"""

    def __init__(self, callback, parameter):
        self._callback = callback
        self._parameter = parameter
        self._more = True
        self._objects = []

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._objects:
            return self.object
        if self._more:
            self._more, page = await self.page()
            self._objects.extend(page)
            if self._objects:
                return self.object
        logging.getLogger('cterasdk.common').debug('Stopping iteration.')
        raise StopAsyncIteration

    @property
    def object(self):
        return self._objects.pop(0)

    @abstractmethod
    async def page(self):
        raise NotImplementedError("Subclass must implemenet the 'page' function")


class QueryAsyncIterator(BaseAsyncIterator):
    """ Asynchronous Objects Iterator """

    async def page(self):
        response = await self._callback(self._parameter)
        self._parameter.increment()
        return response.more, response.objects


class CursorAsyncIterator(BaseAsyncIterator):

    def __init__(self, callback, parameter):
        super().__init__(callback, parameter)
        self._cursor = None

    @property
    def cursor(self):
        return self._parameter.cursor

    async def page(self):
        response = await self._callback(self._parameter)
        self._parameter.cursor = response.cursor
        return response.more, response.objects
