from ..lib.session_base import SessionBase, SessionUser
from .enum import Context, Role


class Session(SessionBase):

    Administration = 'Administration'

    def __init__(self, host, context):
        super().__init__(host)
        self.context = context

    def _do_start_local_session(self, ctera_host):
        tenant = ctera_host.get('/currentPortal') or Session.Administration
        if self.local_auth:
            self.user = SessionUser('$admin', tenant=tenant, role=Role.ReadWriteAdmin)
        else:
            current_session = ctera_host.get('/currentSession')
            self.user = SessionUser(current_session.username, tenant=tenant, role=current_session.role)

    def _do_terminate(self):
        pass

    def update_tenant(self, current_tenant):
        self.user.tenant = current_tenant or Session.Administration

    def is_global_admin(self):
        return self.context == Context.admin

    def in_tenant_context(self):
        return self.tenant() != Session.Administration
