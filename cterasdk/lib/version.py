from .platform import Platform

class Version:

    __instance = None

    @staticmethod 
    def instance():

        if Version.__instance == None:

            Version()

        return Version.__instance

    def __init__(self):

        if Version.__instance != None:

            raise Exception("Version is a singleton class.")

        else:
            
            self.product            = 'Chopin'

            self.product_version    = '3.0'

            self.system             = Platform.instance().os()

            self.machine            = Platform.instance().arch()

            self.header = self.product + '/' + self.product_version + ' (' +  '; '.join([self.system, self.machine])  + ')' + ' ' + 'Python-urllib/' + Platform.instance().python_version()
            
            Version.__instance = self
            
    def as_header(self):
    
        return self.header
    

        

    
        
        
        