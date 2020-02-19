from ..exception import InputError

import logging

from .enum import License

def infer(license):
    
    if License.__dict__.get(license) == None:
        
        logging.getLogger().error('Invalid license type. {0}'.format({'license' : license}))
        
        options = [v for k,v in License.__dict__.items() if not k.startswith('_')]
        
        raise InputError('Invalid license type', license, options)
        
    else:
        
        license = License.__dict__.get(license)
        
        return 'vGateway' + ('' if license == 'EV16' else license[2:])
    
def apply(ctera_host, license):
    
    inferred_license = infer(license)
    
    logging.getLogger().info('Applying license. {0}'.format({'license' : license}))
    
    ctera_host.put('/config/device/activeLicenseType', inferred_license)

    logging.getLogger().info('License applied. {0}'.format({'license' : license}))