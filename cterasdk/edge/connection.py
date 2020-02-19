import logging

def test(CTERAHost):
    
    test_network(CTERAHost)
    
    test_application(CTERAHost)
    
def test_network(CTERAHost):
    
    CTERAHost.test_conn()

def test_application(CTERAHost):
    
    ref = '/nosession/logininfo'
    
    logging.getLogger().debug('Trying to obtain login info. {0}'.format({'ref' : ref}))
    
    response = CTERAHost.get(ref)
    
    logging.getLogger().debug('Successfully obtained login info. {0}'.format({'ref' : ref, 'hostname' : response.hostname}))
    
    return response