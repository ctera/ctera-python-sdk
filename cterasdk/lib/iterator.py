import logging


class Iterator:

    def __init__(self, function, param):
        self.function = function
        self.param = param
        self.hasMore = True
        self.objects = []

    def __iter__(self):
        return self

    def __next__(self):
        if not self.objects:
            if self.hasMore:
                self.hasMore, self.objects = self.function(self.param)
                if not self.hasMore and not self.objects:
                    self.terminate()
                self.param.increment()
            else:
                self.terminate()
        return self.objects.pop(0)

    @staticmethod
    def terminate():
        logging.getLogger().debug('No more objects to return. Stopping iteration.')
        raise StopIteration
