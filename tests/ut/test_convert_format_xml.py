from cterasdk import Object
from tests.ut import base_convert


class TestFormatObjectXML(base_convert.TestXML):

    def test_named_tuple(self):
        o = Object()
        o.name = "alice"
        o.email = "alice.wonderland@microsoft.com"
        o.firstName = "Alice"
        o.lastName = "Wonderland"
        o.company = "Microsoft Corporation"
        o.showTutorial = True
        o.uid = 2156
        o.password = None
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
        self.assertEqual(base_convert.TestXML._toxmlstr(o), user_object)


class TestFormatListValueXML(base_convert.TestXML):

    def test_list_of_int(self):
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.assertEqual(base_convert.TestXML._toxmlstr(values), base_convert.TestXML._format_list_of_values(values))

    def test_list_of_str(self):
        values = ['SATA-' + str(i) for i in range(1, 11)]
        self.assertEqual(base_convert.TestXML._toxmlstr(values), base_convert.TestXML._format_list_of_values(values))


class TestFormatValueXML(base_convert.TestXML):

    def test_int(self):
        value = 1024
        self.assertEqual(base_convert.TestXML._toxmlstr(value), base_convert.TestXML._format_value(value))

    def test_str(self):
        value = 'SATA-1'
        self.assertEqual(base_convert.TestXML._toxmlstr(value), base_convert.TestXML._format_value(value))

    def test_str_with_spaces(self):
        value = 'The quick brown fox jumped over the lazy dog'
        self.assertEqual(base_convert.TestXML._toxmlstr(value), base_convert.TestXML._format_value(value))

    def test_true_bool(self):
        value = True
        self.assertEqual(base_convert.TestXML._toxmlstr(value), base_convert.TestXML._format_value(value))

    def test_false_bool(self):
        value = False
        self.assertEqual(base_convert.TestXML._toxmlstr(value), base_convert.TestXML._format_value(value))

    def test_float(self):
        value = 0.6901
        self.assertEqual(base_convert.TestXML._toxmlstr(value), base_convert.TestXML._format_value(value))
