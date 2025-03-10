# pylint: disable=protected-access
import json

from cterasdk import Object
from tests.ut import base_convert


class TestFormatObjectJSON(base_convert.TestJSON):

    def test_null(self):
        o = Object()
        o.company = None
        self.assertEqual(base_convert.TestJSON._tojsonstr(o), '{"company": null}')

    def test_int(self):
        o = Object()
        o.uid = 2156
        self.assertEqual(base_convert.TestJSON._tojsonstr(o), '{"uid": 2156}')

    def test_str(self):
        o = Object()
        o.name = "alice"
        self.assertEqual(base_convert.TestJSON._tojsonstr(o), '{"name": "alice"}')

    def test_bool_true(self):
        o = Object()
        o.active = True
        self.assertEqual(base_convert.TestJSON._tojsonstr(o), '{"active": true}')

    def test_bool_false(self):
        o = Object()
        o.active = False
        self.assertEqual(base_convert.TestJSON._tojsonstr(o), '{"active": false}')

    def test_list(self):
        o = Object()
        o.drives = ['SATA-' + str(i) for i in range(1, 4)]
        self.assertEqual(base_convert.TestJSON._tojsonstr(o), '{"drives": ["SATA-1", "SATA-2", "SATA-3"]}')

    def test_object(self):
        o = Object()
        o.config = Object()
        o.config.device = Object()
        o.config.device.name = "CTERA"
        o.config.device.uptime = "P0Y0M0DT0H0M24S"
        o.config.device.runningFirmware = "6.0.589.0"
        device_config = '{"config": ' \
            '{"device": ' \
            '{"name": "CTERA", "uptime": "P0Y0M0DT0H0M24S", "runningFirmware": "6.0.589.0"}' \
            '}' \
            '}'
        self.assertEqual(base_convert.TestJSON._tojsonstr(o), device_config)

    def test_sensitive_object(self):
        o = Object()
        o.password = 'secret'
        object_str_json = json.loads(base_convert.TestJSON._tojsonstr(o, False, True))
        self.assertEqual(object_str_json['password'], "*** Protected Value ***")
