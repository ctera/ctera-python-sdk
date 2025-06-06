from .base import CTERAException


class NotFound(CTERAException):
    """ Not found exception """


class AttachEncrypted(CTERAException):
    """ Attach Encrypted exception """

    def __init__(self, encryptionMode, encryptedFolderKey, passPhraseSalt):
        super().__init__()
        self.encryptionMode = encryptionMode
        self.encryptedFolderKey = encryptedFolderKey
        self.passPhraseSalt = passPhraseSalt


class IncorrectPassphrase(CTERAException):
    """ Incorrect Passphrase exception """

    def __init__(self):
        super().__init__('Incorrect passphrase')


class ClocksOutOfSync(CTERAException):
    """ Clocks Out of Sync exception """

    def __init__(self):
        super().__init__('Clocks are out of sync')
