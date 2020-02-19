from ..convert import tojsonstr

import logging

def generate_code(ctera_host, username, tenant):
    
    params = { 'username' : username }
        
    if tenant != None:

        params['portal'] = tenant
        
    logging.getLogger().info('Generating device activation code. {0}'.format({'user' : username, 'portal' : tenant}))

    response = ctera_host.get('/ssoActivation', params)
    
    logging.getLogger().info('Generated device activation code. {0}'.format(tojsonstr(response, False)))

    return response.code