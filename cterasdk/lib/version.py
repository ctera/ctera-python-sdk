from .platform import Platform


class Version:  # pylint: disable=unused-private-member

    __instance = None

    @staticmethod
    def instance():
        if Version.__instance is None:
            Version()
        return Version.__instance

    def __init__(self):
        if Version.__instance is not None:
            raise Exception("Version is a singleton class.")

        self.product = 'Chopin'
        self.product_version = '3.0'
        self.system = Platform.instance().os()
        self.machine = Platform.instance().arch()
        self.header = \
            f"{self.product}/{self.product_version} ({self.system}; {self.machine}) Python-urllib/{Platform.instance().python_version()}"
        Version.__instance = self

    def as_header(self):

        return self.header
