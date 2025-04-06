# pylint: disable=protected-access
from tests.ut.serializers import base


class TestParseObjectXML(base.TestXML):

    def test_named_tuple(self):
        user_object = '<obj>' \
            '<att id="name"><val>alice</val></att>' \
            '<att id="email"><val>alice.wonderland@microsoft.com</val></att>' \
            '<att id="firstName"><val>Alice</val></att>' \
            '<att id="lastName"><val>Wonderland</val></att>' \
            '<att id="company"><val>Microsoft Corporation</val></att>' \
            '<att id="showTutorial"><val>true</val></att>' \
            '<att id="uid"><val>2156</val></att>' \
            '<att id="password" />' \
            '</obj>'
        o = base.TestXML._fromxmlstr(user_object)
        self.assertEqual(o.name, 'alice')
        self.assertEqual(o.email, 'alice.wonderland@microsoft.com')
        self.assertEqual(o.firstName, 'Alice')
        self.assertEqual(o.lastName, 'Wonderland')
        self.assertEqual(o.company, 'Microsoft Corporation')
        self.assertEqual(o.showTutorial, True)
        self.assertEqual(o.uid, 2156)
        self.assertEqual(o.password, None)

    def test_list_of_objects(self):
        disks = '<list key="name">' \
            '<obj class="DiskStatus" uuid="ba94e323-e988-4c3d-a353-3fc5402a8614">' \
            '<att id="name">' \
            '<val>SATA1</val>' \
            '</att>' \
            '<att id="isCtera">' \
            '<val>true</val>' \
            '</att>' \
            '<att id="serial">' \
            '<val>JPW9K0N01AU4HL</val>' \
            '</att>' \
            '<att id="firmware">' \
            '<val>JP4OA3EA</val>' \
            '</att>' \
            '<att id="logicalCapacity">' \
            '<val>952830</val>' \
            '</att>' \
            '</obj>' \
            '<obj class="DiskStatus" uuid="3c875a08-4de9-461f-8b52-a7e3dfb1bf2d">' \
            '<att id="name">' \
            '<val>SATA2</val>' \
            '</att>' \
            '<att id="isCtera">' \
            '<val>false</val>' \
            '</att>' \
            '<att id="serial">' \
            '<val>JPW9K0N01968XL</val>' \
            '</att>' \
            '<att id="firmware">' \
            '<val>JP4OA3EA</val>' \
            '</att>' \
            '<att id="logicalCapacity">' \
            '<val>952830</val>' \
            '</att>' \
            '</obj>' \
            '</list>'
        o = base.TestXML._fromxmlstr(disks)
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


class TestParseListValueXML(base.TestXML):

    def test_list_of_int(self):
        original_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        formatted_values = base.TestXML._format_list_of_values(original_values)
        self.assertEqual(base.TestXML._fromxmlstr(formatted_values), original_values)

    def test_list_of_str(self):
        original_values = ['SATA-' + str(i) for i in range(1, 11)]
        formatted_values = base.TestXML._format_list_of_values(original_values)
        self.assertEqual(base.TestXML._fromxmlstr(formatted_values), original_values)


class TestParseValueXML(base.TestXML):

    def test_int(self):
        original_value = 1024
        formatted_value = base.TestXML._format_value(original_value)
        self.assertEqual(base.TestXML._fromxmlstr(formatted_value), original_value)

    def test_str(self):
        original_value = 'SATA-1'
        formatted_value = base.TestXML._format_value(original_value)
        self.assertEqual(base.TestXML._fromxmlstr(formatted_value), original_value)

    def test_true_bool(self):
        original_value = True
        formatted_value = base.TestXML._format_value(original_value)
        self.assertEqual(base.TestXML._fromxmlstr(formatted_value), original_value)

    def test_false_bool(self):
        original_value = False
        formatted_value = base.TestXML._format_value(original_value)
        self.assertEqual(base.TestXML._fromxmlstr(formatted_value), original_value)

    def test_float(self):
        original_value = 0.6901
        formatted_value = base.TestXML._format_value(original_value)
        self.assertEqual(base.TestXML._fromxmlstr(formatted_value), original_value)
