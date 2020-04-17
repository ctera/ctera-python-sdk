from ..lib.session_base import SessionBase, SessionUser
from .enum import Context


class Session(SessionBase):

    def __init__(self, host, context):
        super().__init__(host)
        self.context = context

    def _do_start_local_session(self, ctera_host):
        tenant = ctera_host.get('/currentPortal') or 'Administration'
        current_session = ctera_host.get('/currentSession')
        self.user = SessionUser(current_session.username, tenant=tenant, role=current_session.role)

    def _do_terminate(self):
        pass

    def update_tenant(self, current_tenant):
        self.user.tenant = current_tenant or 'Administration'

    def global_admin(self):
        return self.context == Context.admin
