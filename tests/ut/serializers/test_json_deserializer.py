from cterasdk import fromjsonstr
from tests.ut.serializers import base


class TestParseObjectJSON(base.TestJSON):

    def test_json_object(self):
        user_object = '{' \
            '"name": "alice", ' \
            '"email": "alice.wonderland@microsoft.com", ' \
            '"firstName": "Alice", ' \
            '"lastName": "Wonderland", ' \
            '"company": "Microsoft Corporation", ' \
            '"showTutorial": true, ' \
            '"uid": 2156,' \
            '"password" : null' \
            '}'
        o = fromjsonstr(user_object)
        self.assertEqual(o.name, 'alice')
        self.assertEqual(o.email, 'alice.wonderland@microsoft.com')
        self.assertEqual(o.firstName, 'Alice')
        self.assertEqual(o.lastName, 'Wonderland')
        self.assertEqual(o.company, 'Microsoft Corporation')
        self.assertEqual(o.showTutorial, True)
        self.assertEqual(o.uid, 2156)
        self.assertEqual(o.password, None)

    def test_json_array(self):
        disks = '['\
            '{"name": "SATA1", "isCtera": true, "serial": "JPW9K0N01AU4HL", "firmware": "JP4OA3EA", "logicalCapacity": 952830}, ' \
            '{"name": "SATA2", "isCtera": false, "serial": "JPW9K0N01968XL", "firmware": "JP4OA3EA", "logicalCapacity": 952830}' \
            ']'
        o = fromjsonstr(disks)
        self.assertEqual(o[0].name, 'SATA1')
        self.assertEqual(o[0].isCtera, True)
        self.assertEqual(o[0].serial, 'JPW9K0N01AU4HL')
        self.assertEqual(o[0].firmware, 'JP4OA3EA')
        self.assertEqual(o[0].logicalCapacity, 952830)

        self.assertEqual(o[1].name, 'SATA2')
        self.assertEqual(o[1].isCtera, False)
        self.assertEqual(o[1].serial, 'JPW9K0N01968XL')
        self.assertEqual(o[1].firmware, 'JP4OA3EA')
        self.assertEqual(o[1].logicalCapacity, 952830)
