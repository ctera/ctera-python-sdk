from . import session

from ..exception import CTERAException

import logging

def login(ctera_host, username, password):
    
    host = ctera_host.host()
    
    try:
    
        ctera_host.form_data('/login', {'username' : username, 'password' : password})
        
        logging.getLogger().info("User logged in. {0}".format({'host' : host, 'user': username}))
        
        session.start_local_session(ctera_host, host, username)

    except CTERAException as error:
        
        logging.getLogger().error("Login failed. {0}".format({'host' : host, 'user': username}))
        
        raise error
            
def logout(ctera_host):
    
    try:
        
        ctera_host.form_data('/logout', {'foo' : 'bar'})
        
        session.terminate(ctera_host)
        
        logging.getLogger().info("User logged out. {0}".format({'host' : ctera_host.host()}))
        
    except CTERAException as error:
        
        raise error