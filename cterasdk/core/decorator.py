import logging
import asyncio
import functools
from contextlib import contextmanager


logger = logging.getLogger('cterasdk.core')


def update_current_tenant(execute_request):
    if asyncio.iscoroutinefunction(execute_request):
        @functools.wraps(execute_request)
        async def execute_and_update(self, tenant):
            with update_current_session(self, tenant):
                response = await execute_request(self, tenant)
            return response
    else:
        @functools.wraps(execute_request)
        def execute_and_update(self, tenant):
            with update_current_session(self, tenant):
                response = execute_request(self, tenant)
            return response
    return execute_and_update


@contextmanager
def update_current_session(core, tenant):
    yield
    tenant = tenant if tenant else 'Administration'
    logger.debug('Updating current session. Tenant: %s', tenant)
    core.session().update_current_tenant(tenant)
    logger.debug('Updated current session. Tenant: %s', tenant)
