from unittest import mock

from cterasdk.edge import snmp
from cterasdk.edge.enum import Mode
from cterasdk.common import Object
from tests.ut import base_edge


class TestEdgeSNMP(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._snmp_default_port = 161
        self._snmp_custom_port = 361
        self._snmp_community_str = 'community_string'
        self._snmp_v3_user = 'user'
        self._snmp_v3_pass = 'pass'

    def test_get_configuration(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = snmp.SNMP(self._filer).get_configuration()
        self._filer.get.assert_called_once_with('/config/snmp')
        self._assert_equal_objects(ret, get_response)

    def test_enable_snmp_default_params(self):
        self._init_filer()
        snmp.SNMP(self._filer).enable()
        self._filer.put.assert_called_once_with('/config/snmp', mock.ANY)

        expected_param = self._get_snmp_object()
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_enable_snmp_with_port_and_community_str(self):
        self._init_filer()
        snmp.SNMP(self._filer).enable(self._snmp_custom_port, self._snmp_community_str)
        self._filer.put.assert_called_once_with('/config/snmp', mock.ANY)

        expected_param = self._get_snmp_object(port=self._snmp_custom_port, community_str=self._snmp_community_str)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_enable_snmp_v3(self):
        self._init_filer()
        snmp.SNMP(self._filer).enable(username=self._snmp_v3_user, password=self._snmp_v3_pass)
        self._filer.put.assert_called_once_with('/config/snmp', mock.ANY)

        expected_param = self._get_snmp_object(username=self._snmp_v3_user, password=self._snmp_v3_pass)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_disable_snmp(self):
        self._init_filer()
        snmp.SNMP(self._filer).disable()
        self._filer.put.assert_called_once_with('/config/snmp/mode', Mode.Disabled)

    def test_modify_success(self):
        self._init_filer(get_response=self._get_snmp_object())
        snmp.SNMP(self._filer).modify(self._snmp_custom_port, self._snmp_community_str,
                                      self._snmp_v3_user, self._snmp_v3_pass)
        self._filer.get.assert_called_once_with('/config/snmp')
        self._filer.put.assert_called_once_with('/config/snmp', mock.ANY)
        expected_param = self._get_snmp_object(self._snmp_custom_port, self._snmp_community_str, self._snmp_v3_user, self._snmp_v3_pass)
        actual_param = self._filer.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def _get_snmp_object(self, port=None, community_str=None, username=None, password=None):
        param = Object()
        param.mode = Mode.Enabled
        param.port = self._snmp_default_port if port is None else port
        param.readCommunity = community_str
        if username is not None and password is not None:
            param.snmpV3 = Object()
            param.snmpV3.mode = Mode.Enabled
            param.snmpV3.username = username
            param.snmpV3.password = password
        return param
