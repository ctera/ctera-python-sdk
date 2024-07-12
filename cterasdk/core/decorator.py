import logging
import functools


def update_current_tenant(execute_request):
    @functools.wraps(execute_request)
    def execute_and_update(self, tenant):
        logging.getLogger('cterasdk.core').debug('Updating current tenant. %s', {'tenant': tenant})
        return_value = execute_request(self, tenant)
        self.session().update_current_tenant(tenant)
        logging.getLogger('cterasdk.core').debug('Updated current tenant. %s', {'tenant': tenant})
        return return_value
    return execute_and_update
