# pylint: disable=too-many-instance-attributes
import copy
import json


class Object:
    _sdk_hidden = [
        'password',
        'awsSecretKey',
        'sharedSecret',
        'passPhraseSalt',
        'encPassphrase',
        'encryptedFolderKey',
        'oldPassword',
        'newPassword',
        'secretkey',
        'activationCode'
    ]

    def __str__(self):
        def to_protected_dict(o):
            ret = copy.deepcopy(o.__dict__)
            for key in o._sdk_hidden:  # pylint: disable=protected-access
                if key in ret:
                    ret[key] = '*** The Value if Hidden by the SDK ***'
            return ret
        return json.dumps(self, default=to_protected_dict, indent=5)
