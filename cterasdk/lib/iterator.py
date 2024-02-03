import logging


class Iterator:
    """ Objects Iterator """

    def __init__(self, function, param):
        self._function = function
        self._param = param
        self._hasMore = True
        self._objects = []

    def __iter__(self):
        return self

    def __next__(self):
        if not self._objects:
            if self._hasMore:
                self._hasMore, self._objects = self._function(self._param)
                if not self._hasMore and not self._objects:
                    self._terminate()
                self._param.increment()
            else:
                self._terminate()
        return self._objects.pop(0)

    @staticmethod
    def _terminate():
        logging.getLogger().debug('No more objects to return. Stopping iteration.')
        raise StopIteration
