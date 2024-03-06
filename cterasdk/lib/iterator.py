import logging


import logging
from abc import abstractmethod


class BaseIterator:
    """Abstract Iterator"""

    def __init__(self, callback, parameter):
        self._callback = callback
        self._parameter = parameter
        self._more = True
        self._objects = []

    def __iter__(self):
        return self
    
    def __next__(self):
        if self._objects:
            return self.object
        if self._more:
            self._more, self._page = self.page()
            self._objects.extend(self._page)
            if self._objects:
                return self.object
        logging.getLogger().debug('Stopping iteration.')
        raise StopIteration
    
    @property
    def object(self):
        return self._objects.pop(0)

    @abstractmethod
    def page(self):
        raise NotImplementedError("Subclass must implemenet the 'page' function")


class QueryIterator(BaseIterator):
    """ Objects Iterator """

    def __init__(self, callback, parameter):
        super().__init__(callback, parameter)

    def page(self):
        response = self._callback(self._parameter)
        self._parameter.increment()
        return response.more, response.objects
    

class CursorIterator(BaseIterator):

    def __init__(self, callback, parameter):
        super().__init__(callback, parameter)
        self._cursor = None

    @property
    def cursor(self):
        return self._cursor

    def page(self):
        response = self._callback(self._parameter)
        self._parameter.cursor = response.cursor
        return response.more, response.objects


class BaseResponse:

    def __init__(self, response):
        self._response = response

    @property
    @abstractmethod
    def more(self):
        raise NotImplementedError("Subclass must implement the 'more' method")
    
    @property
    @abstractmethod
    def objects(self):
        raise NotImplementedError("Subclass must implement the 'objects' method")
    

class DefaultResponse(BaseResponse):

    @property
    @abstractmethod
    def more(self):
        return self._response.hasMore
    
    @property
    @abstractmethod
    def objects(self):
        return self._response.objects
    
    
class QueryLogsResponse(DefaultResponse):

    @property
    def objects(self):
        return self._response.logs
    

class CursorResponse(BaseResponse):

    @property
    def more(self):
        return self._response.has_more
    
    @property
    def objects(self):
        return self._response.entries
    
    @property
    def cursor(self):
        return self._response.cursor