class Registry:

    __instance = None

    @staticmethod
    def instance():
        if Registry.__instance is None:
            Registry()
        return Registry.__instance

    def __init__(self):
        if Registry.__instance is not None:
            raise Exception("Registry is a singleton class.")
        self.registry = {}
        Registry.__instance = self

    def register(self, key, value):
        self.registry[key] = value

    def get(self, key):
        return self.registry.get(key)

    def remove(self, key):
        return self.registry.pop(key, None)
