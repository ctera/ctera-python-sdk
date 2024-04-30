import logging
import functools

from ..exceptions import CTERAException


def authenticated(execute_request):
    @functools.wraps(execute_request)
    def authenticate_then_execute(self, *args, **kwargs):
        if callable(self._authenticator) and self._authenticator(self._builder(args[0])):  # pylint: disable=protected-access
            return execute_request(self, *args, **kwargs)
        logging.getLogger('cterasdk.common').error('Not logged in.')
        raise CTERAException('Not logged in')
    return authenticate_then_execute
