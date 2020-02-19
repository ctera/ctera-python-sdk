from .enum import Mode, CIFSPacketSigning

from ..exception import CTERAException, InputError

import logging

def enable(ctera_host):
    
    logging.getLogger().info('Enabling SMB server.')
    
    ctera_host.put('/config/fileservices/cifs/mode', Mode.Enabled)
    
    logging.getLogger().info('SMB server enabled.')
    
def enable_abe(ctera_host):
    
    logging.getLogger().info('Enabling ABE.')
    
    ctera_host.put('/config/fileservices/cifs/hideUnreadable', True)
    
    logging.getLogger().info('Access Based Enumeration (ABE) enabled.')
    
def disable_abe(ctera_host):
    
    logging.getLogger().info('Disabling ABE.')
    
    ctera_host.put('/config/fileservices/cifs/hideUnreadable', False)
    
    logging.getLogger().info('Access Based Enumeration (ABE) disabled.')
    
def set_packet_signing(ctera_host, packet_signing):
    
    options = [v for k,v in CIFSPacketSigning.__dict__.items() if not k.startswith('_')]
    
    if not packet_signing in options:
        
        raise InputError('Invalid packet signing option', packet_signing, options)
    
    logging.getLogger().info('Updating SMB packet signing configuration.')
    
    try:
    
        ctera_host.put('/config/fileservices/cifs/packetSigning', packet_signing)
        
        logging.getLogger().info('SMB packet signing configuration updated. {0}'.format({'packet_signing' : packet_signing}))
        
    except CTERAException as error:
        
        logging.getLogger().error('Failed to update SMB packet signing configuration.')
        
        raise CTERAException('Invalid packet signing co', error)
    
def disable(ctera_host):
    
    logging.getLogger().info('Disabling SMB server.')
    
    ctera_host.put('/config/fileservices/cifs/mode', Mode.Disabled)
    
    logging.getLogger().info('SMB server disabled.')