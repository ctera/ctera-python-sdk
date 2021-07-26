import platform


class Platform:  # pylint: disable=unused-private-member

    __instance = None

    @staticmethod
    def instance():
        if Platform.__instance is None:
            Platform()
        return Platform.__instance

    def __init__(self):
        if Platform.__instance is not None:
            raise Exception("Platform is a singleton class.")
        self.hostname = platform.node()
        self.operating_system = platform.system()
        self.release = platform.release()
        self.machine = platform.machine()
        self.python_major, self.python_minor, self.python_micro = platform.python_version_tuple()
        Platform.__instance = self

    def arch(self):
        return self.machine

    def os(self):
        return ' '.join([self.operating_system, str(self.release)])

    def python_version(self):
        return '.'.join([self.python_major, self.python_minor, self.python_micro])
