from ..lib.session_base import SessionBase, SessionUser, SessionHostType
from .enum import Context, Role


class PortalUser(SessionUser):

    def __init__(self, name, tenant, role):
        super().__init__(name)
        self.tenant = tenant
        self.role = role


class Session(SessionBase):

    Administration = 'Administration'

    def __init__(self, host, context):
        super().__init__(host, SessionHostType.Portal)
        self.context = context
        self.local_auth = False

    def _do_start_local_session(self, CTERA_Host):
        tenant = CTERA_Host.api.get('/currentPortal') or Session.Administration
        self.set_version(CTERA_Host.api.get('/version'))
        if self.local_auth:
            self.user = PortalUser('$admin', tenant=tenant, role=Role.ReadWriteAdmin)
        else:
            current_session = CTERA_Host.api.get('/currentSession')
            self.user = PortalUser(current_session.username, tenant=tenant, role=current_session.role)

    def _do_terminate(self):
        pass

    def update_tenant(self, current_tenant):
        self.user.tenant = current_tenant or Session.Administration

    def is_global_admin(self):
        return self.context == Context.admin

    def is_local_auth(self):
        return self.local_auth

    def in_tenant_context(self):
        return self.tenant() != Session.Administration
