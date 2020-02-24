import functools
import logging

from ..exception import CTERAException


def authenticated(function):

    @functools.wraps(function)
    def check_authenticated_and_call(self, *args):
        session = self.session()

        if session.authenticated():
            return function(self, *args)
        if is_nosession(function, args[0]):
            return function(self, *args)
        logging.getLogger().error('Not logged in.')
        raise CTERAException('Not logged in')

    return check_authenticated_and_call


def is_nosession(function, path):
    return function.__name__ == 'get' and path.startswith('/nosession')
