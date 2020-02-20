class Command:

    def __init__(self, cmd, *args):
        self._cmd = cmd
        self._args = args

    def __call__(self, *args):
        return self._cmd(*(self._args + args))
