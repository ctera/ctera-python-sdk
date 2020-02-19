import sys

import logging

class Logging:
    
    __instance = None

    @staticmethod 
    def get():

        if Logging.__instance == None:

            Logging()

        return Logging.__instance

    def __init__(self):

        if Logging.__instance != None:

            raise Exception("You must invoke Logging.get()")

        else:
            
            disabled    = logconf['disabled']
            
            level       = logconf['level']
            
            fmt         = logconf['fmt']
            
            df          = logconf['df']
            
            Logging.__instance = self
            
            self._logconf(fmt, df)
            
            logger = logging.getLogger()
            
            logger.disabled = disabled
            
            logger.level    = level
            
    def _logconf(self, fmt, df):
        
        logging.basicConfig(format = fmt, datefmt = df, stream = sys.stdout)
    
    def disable(self):
        
        logging.getLogger().disabled = True
    
    def enable(self):
        
        logging.getLogger().disabled = False
    
    def setLevel(self, level):
        
        logging.getLogger().setLevel(level)
    
    def fmt(self):
        
        return logconf['fmt']
    
    def df(self):
        
        return logconf['df']

logconf = dict(
    
    disabled = False,

    level = logging.INFO,
    
    fmt   = '%(asctime)s,%(msecs)3d %(levelname)7s [%(filename)s:%(lineno)d] [%(funcName)s] - %(message)s',
    
    df    = '%Y-%m-%d %H:%M:%S'

)

http = dict(

    timeout = 20,          # http client timeout (seconds)
    
    retries = 3,           # handle connection timeout
    
    ssl = 'Consent',       # ['Consent', 'Trust']
    
    verbose = False        # include request info on error

)

connect = dict(

    ssl = 'Consent'        # ['Consent', 'Trust']

)

filesystem = dict(

    dl  = '~/Downloads'
    
)

transcript = dict(

    disabled = True
    
)

