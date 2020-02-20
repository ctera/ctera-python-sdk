import functools
import logging

from ..exception import CTERAException


def authenticated(function):

    @functools.wraps(function)
    def check_authenticated_and_call(self, *args):
        session = self.session()
        if session.authenticated():
            return function(self, *args)

        if session.initializing():
            return function(self, *args)

        logging.getLogger().error('Not logged in.')
        raise CTERAException('Not logged in')

    return check_authenticated_and_call


def update_current_tenant(function):

    @functools.wraps(function)
    def call_and_update_current_tenant(self, *args):
        ret = function(self, *args)

        path = args[0]
        if path == '/currentPortal':
            tenant = args[1]
            logging.getLogger().debug('Updating current tenant. %s', {'tenant' : tenant})

            self.session().update_tenant(tenant)

            logging.getLogger().debug('Updated current tenant. %s', {'tenant' : tenant})

        return ret

    return call_and_update_current_tenant

#ValidIpAddressRegex = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$";

#ValidHostnameRegex = "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$";
