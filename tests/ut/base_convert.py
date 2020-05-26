from cterasdk import fromxmlstr, toxmlstr, tojsonstr
from tests.ut import base


class TestJSON(base.BaseTest):

    @staticmethod
    def _tojsonstr(value, pretty_print=False, no_log=False):
        return tojsonstr(value, pretty_print, no_log)


class TestXML(base.BaseTest):

    @staticmethod
    def _format_list_of_values(values):
        list_of_values = ''
        if values:
            for value in values:
                list_of_values = list_of_values + TestXML._format_value(value)
            return '<list>%s</list>' % list_of_values
        return '<list />'

    @staticmethod
    def _format_value(value):
        if isinstance(value, bool):
            value = str(value).lower()
        return '<val>%s</val>' % value

    @staticmethod
    def _fromxmlstr(value):
        return fromxmlstr(value)

    @staticmethod
    def _toxmlstr(value):
        return toxmlstr(value).decode('utf-8')
