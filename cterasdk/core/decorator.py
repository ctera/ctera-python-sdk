import logging
import functools


def update_current_tenant(execute_request):
    @functools.wraps(execute_request)
    def execute_and_update(self, tenant):
        logging.getLogger().debug('Updating current tenant. %s', {'tenant': tenant})
        return_value = execute_request(self, tenant)
        self.session().update_tenant(tenant)
        logging.getLogger().debug('Updated current tenant. %s', {'tenant': tenant})
        return return_value
    return execute_and_update
