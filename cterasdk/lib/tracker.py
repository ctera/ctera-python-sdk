from ..exception import CTERAException

import logging

import time

class ErrorStatus(CTERAException):
    
    def __init__(self, status):
        
        self.status = status

class StatusTracker:
    
    def __init__(self, CTERAHost, ref, success, progress, transient, failure, retries, seconds):
        
        self.CTERAHost = CTERAHost
        
        self.ref = ref
        
        self.success = success
        
        self.progress = progress
        
        self.transient = transient
        
        self.failure = failure
        
        self.retries = retries
        
        self.seconds = seconds
        
        self.attempt = 0
        
    def track(self):
        
        running = True
        
        while running:
            
            logging.getLogger().debug('Retrieving status. {0}'.format({'ref' : self.ref, 'attempt' : (self.attempt + 1)}))
            
            self.status = self.CTERAHost.get(self.ref)
            
            logging.getLogger().debug('Current status. {0}'.format({'ref' : self.ref, 'status' : self.status}))
        
            self.increment()
            
            running = self.running()
                       
        return self.resolve()
            
    def resolve(self):
        
        if self.successful():
            
            logging.getLogger().debug('Success. {0}'.format({'ref' : self.ref, 'status' : self.status}))
            
            return self.status
        
        elif self.failed():
            
            logging.getLogger().debug('Failure. {0}'.format({'ref' : self.ref, 'status' : self.status}))
            
            raise ErrorStatus(self.status)
            
        else:
            
            logging.getLogger().debug('Unknown status. {0}'.format({'ref' : self.ref, 'status' : self.status}))
            
            raise CTERAException('Unknown status', None, status = self.status)
        
    def successful(self):
        
        return self.status in self.success
        
    def running(self):
        
        if self.status in self.progress:
            
            logging.getLogger().debug('In progress. {0}'.format({'ref' : self.ref, 'status' : self.status}))
            
            return True
            
        elif self.status in self.transient:
            
            logging.getLogger().debug('Transient state. {0}'.format({'ref' : self.ref, 'status' : self.status}))
            
            return True
            
        else:
            
            logging.getLogger().debug('End state. {0}'.format({'ref' : self.ref, 'status' : self.status}))
            
            return False
    
    def failed(self):
        
        return self.status in self.failure
    
    def increment(self):
        
        self.attempt = self.attempt + 1
        
        if not self.attempt < self.retries:
            
            logging.getLogger().error('Status did not meet success criteria.'.format({'ref' : self.ref, 'status' : self.status}))
            
            raise CTERAException('Timed out. Status did not meet success criteria', None, ref = self.ref, status = self.status)
        
        logging.getLogger().debug('Sleep. {0}'.format({'seconds' : self.seconds}))
        
        time.sleep(self.seconds)

def track(CTERAHost, ref, success, progress, transient, failure, retries = 300, seconds = 1):
    
    tracker = StatusTracker(CTERAHost, ref, success, progress, transient, failure, retries, seconds)
    
    return tracker.track()
        