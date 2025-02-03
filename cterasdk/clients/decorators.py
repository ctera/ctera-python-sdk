import logging
import functools

from ..exceptions import SessionExpired, NotLoggedIn


def authenticated(execute_request):
    @functools.wraps(execute_request)
    def authenticate_then_execute(self, *args, **kwargs):
        if callable(self._authenticator) and self._authenticator(self._builder(args[0])):  # pylint: disable=protected-access
            try:
                return execute_request(self, *args, **kwargs)
            except SessionExpired:
                logging.getLogger('cterasdk.common').error('Session expired.')
                self.cookies.clear()
        logging.getLogger('cterasdk.common').error('Not logged in.')
        raise NotLoggedIn()
    return authenticate_then_execute
