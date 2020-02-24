import logging

from ..convert import tojsonstr


def generate_code(ctera_host, username, tenant):
    params = {'username': username}

    if tenant is not None:
        params['portal'] = tenant

    logging.getLogger().info('Generating device activation code. %s', {'user': username, 'portal': tenant})

    response = ctera_host.get('/ssoActivation', params)

    logging.getLogger().info('Generated device activation code. %s', tojsonstr(response, False))

    return response.code
