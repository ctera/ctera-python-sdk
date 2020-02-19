from ..common import Object

from ..exception import HostUnreachable, ExhaustedException

import logging

import time

def reboot(CTERAHost, wait):
    
    logging.getLogger().info("Rebooting device. {0}".format({'host' : CTERAHost.host()}))

    CTERAHost.execute("/status/device", "reboot", None)

    if wait:

        boot = Boot(CTERAHost)
        
        boot.wait()

def shutdown(ctera_host):
    
    ctera_host.execute("/status/device", "poweroff", None)

def reset(CTERAHost, wait):
    
    CTERAHost.execute("/status/device", "reset2default", None)

    logging.getLogger().info("Resetting device to default settings. {0}".format({'host' : CTERAHost.host()}))

    if wait:

        boot = Boot(CTERAHost)
        
        boot.wait()
        
class Boot:
    
    def __init__(self, CTERAHost, retries = 60, seconds = 5):
        
        self.CTERAHost = CTERAHost
        
        self.retries = retries
        
        self.seconds = seconds
        
        self.attempt = 0
        
    def wait(self):
        
        while True:
                    
            try:
            
                self.increment()
                
                logging.getLogger().debug('Checking if device is up and running. {0}'.format({'attempt' : self.attempt}))
            
                self.CTERAHost.test()
                
                logging.getLogger().info("Device is back up and running.")
                
                break
                
            except (HostUnreachable, ExhaustedException) as e:
                
                logging.getLogger().debug('Exception. {0}'.format({'exception' : e.classname, 'message' : e.message}))
        
    def increment(self):
        
        self.attempt = self.attempt + 1
        
        if not self.attempt < self.retries:
            
            self.unreachable()
        
        logging.getLogger().debug('Sleep. {0}'.format({'seconds' : self.seconds}))
        
        time.sleep(self.seconds)
        
    def unreachable(self):
        
        scheme  = self.CTERAHost.scheme()
            
        host    = self.CTERAHost.host()

        port    = self.CTERAHost.port()

        logging.getLogger().error('Timed out. Could not reach host'.format({'scheme' : scheme, 'host' : host, 'port' : port}))

        raise HostUnreachable(None, host, port, scheme)