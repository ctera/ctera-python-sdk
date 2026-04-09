import logging
from .base import BaseSession, BaseUser, AccountType, InternalUser
from .types import Product
from ...common import Object
from ...core.enum import Administrators, Context


class ExternalUser(BaseUser):
    """External User"""

    def __init__(self):
        super().__init__(AccountType.External)


class PortalUser(InternalUser):
    """Local User"""

    def __init__(self, name, domain, tenant, role, authorizations):
        super().__init__(name, domain)
        self.tenant = tenant
        self.role = Role(role, authorizations)


class Role(Object):
    """User Role"""

    def __init__(self, name, authorizations):
        super().__init__()
        self.name = name
        if authorizations:
            self.access_end_user_folders = authorizations.access_end_user_folders


class Session(BaseSession):

    Administration = 'Administration'

    def __init__(self, address, context):
        super().__init__(address, Product.Portal)
        self.context = context

    def _start_session(self, session):
        account = None
        if session.context != Context.Invitations:
            logging.getLogger('cterasdk.core').debug('Starting Session.')
            user_session = session.api.get('/currentSession')
            current_tenant = session.api.get('/currentPortal') or Session.Administration
            software_version = session.api.get('/version')
            authorizations = session.roles.get(user_session.role) if user_session.role in Administrators else None
            account = PortalUser(user_session.username, user_session.domain, current_tenant or Session.Administration,
                                 user_session.role, authorizations)
            self._update_software_version(software_version)
        else:
            account = ExternalUser()
        self._update_account(account)

    async def _async_start_session(self, session):
        logging.getLogger('cterasdk.core').debug('Starting Session.')
        account = None
        if session.context != Context.Invitations:
            user_session = await session.v1.api.get('/currentSession')
            current_tenant = session.v1.api.get('/currentPortal')
            software_version = session.v1.api.get('/version')
            authorizations = await session.roles.get(user_session.role) if user_session.role in Administrators else None
            account = PortalUser(user_session.username, user_session.domain, await current_tenant or Session.Administration,
                                 user_session.role, authorizations)
            self._update_software_version(await software_version)
        else:
            account = ExternalUser()
        self._update_account(account)

    def _stop_session(self):  # pylint: disable=no-self-use
        logging.getLogger('cterasdk.core').debug('Stopping Session.')

    def current_tenant(self):
        return self.account.tenant if self.account else None

    def update_current_tenant(self, current_tenant):
        self.account.tenant = current_tenant or Session.Administration

    def in_tenant_context(self):
        return self.current_tenant() != Session.Administration
