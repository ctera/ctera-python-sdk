import json

from cterasdk.common.object import Object
from tests.ut import base


class TestCommonObject(base.BaseTest):
    def test_str(self):
        o = Object()
        o.user = 'user'
        o.password = 'password'
        object_str = str(o)
        object_str_json = json.loads(object_str)
        self.assertEqual(object_str_json['user'], o.user)
        self.assertEqual(object_str_json['password'], '*** The Value is Hidden by the SDK ***')
