import logging

from ..common import Object
from .enum import Context


def inactive_session(Portal):
    session = Session(Portal.host(), Portal.context)
    Portal.register_session(session)


def activate(Portal):
    session = Portal.session()
    session.initialize()

    tenant = obtain_tenant(Portal)
    user, role = obtain_user(Portal)
    session.activate(tenant, user, role)


def terminate(Portal):
    inactive_session(Portal)


def obtain_user(CTERAHost):
    logging.getLogger().debug('Obtaining current user session.')

    current_session = CTERAHost.get('/currentSession')

    logging.getLogger().debug('Obtained current user session.')

    return (current_session.username, current_session.role)


def obtain_tenant(CTERAHost):
    logging.getLogger().debug('Obtaining current tenant.')

    current_tenant = CTERAHost.get('/currentPortal')

    logging.getLogger().debug('Obtained current tenant. %s', {'name': current_tenant})

    return current_tenant


class SessionStatus:
    Initializing = 'Initializing'
    Inactive = 'Inactive'
    Active = 'Active'


class Session(Object):

    def __init__(self, host, context):
        self.host = host
        self.context = context
        self.status = SessionStatus.Inactive
        self.current_tenant = None
        self.user = None

    def initialize(self):
        self.status = SessionStatus.Initializing

    def activate(self, tenant, user, role):
        self.update_tenant(tenant)

        self.user = Object()
        self.user.name = user
        self.user.role = role

        self.status = SessionStatus.Active

    def update_tenant(self, current_tenant):
        if not current_tenant:
            self.current_tenant = 'Administration'
        else:
            self.current_tenant = current_tenant

    def user_name(self):
        return self.user.name

    def global_admin(self):
        return self.context == Context.admin

    def tenant(self):
        return self.current_tenant

    def initializing(self):
        return self.status == SessionStatus.Initializing

    def authenticated(self):
        return self.status == SessionStatus.Active

    def whoami(self):
        print(self)
