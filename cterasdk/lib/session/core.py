import logging
from .base import BaseSession, BaseUser
from .types import Product


class PortalUser(BaseUser):
    """Local User"""

    def __init__(self, name, domain, tenant, role):
        super().__init__(name, domain)
        self.tenant = tenant
        self.role = role


class Session(BaseSession):

    Administration = 'Administration'

    def __init__(self, address, context):
        super().__init__(address, Product.Portal)
        self.context = context

    def _start_session(self, session):
        logging.getLogger('cterasdk.core').debug('Starting Session.')
        current_session = session.api.get('/currentSession')
        current_tenant = session.api.get('/currentPortal') or Session.Administration
        software_version = session.api.get('/version')
        self._update_session(current_session, current_tenant, software_version)

    async def _async_start_session(self, session):
        logging.getLogger('cterasdk.core').debug('Starting Session.')
        current_session = session.v1.api.get('/currentSession')
        current_tenant = session.v1.api.get('/currentPortal')
        software_version = session.v1.api.get('/version')
        self._update_session(await current_session, await current_tenant or Session.Administration, await software_version)

    def _update_session(self, current_session, current_tenant, software_version):
        self._update_account(
            PortalUser(
                current_session.username,
                current_session.domain,
                current_tenant,
                current_session.role
            )
        )
        self._update_software_version(software_version)

    def _stop_session(self):  # pylint: disable=no-self-use
        logging.getLogger('cterasdk.core').debug('Stopping Session.')

    def current_tenant(self):
        return self.account.tenant if self.account else None

    def update_current_tenant(self, current_tenant):
        self.account.tenant = current_tenant or Session.Administration

    def in_tenant_context(self):
        return self.current_tenant() != Session.Administration
