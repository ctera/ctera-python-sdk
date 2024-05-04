from unittest import mock

import munch
from cterasdk.core import syslog
from cterasdk.core.enum import Mode, IPProtocol, Severity
from cterasdk import exceptions, Object
from tests.ut import base_core


class TestCoreSyslog(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._server = 'abc.def.ghi'
        self._port = 514

    def test_is_enabled(self):
        for enabled in [True, False]:
            self._init_global_admin(get_response=Mode.Enabled if True else Mode.Disabled)
            ret = syslog.Syslog(self._global_admin).is_enabled()
            self._global_admin.api.get.assert_called_once_with('/settings/logsSettings/syslogConfig/mode')
            self.assertEqual(ret, enabled)

    def test_get_configuration(self):
        syslog_config = 'Config'
        self._init_global_admin(get_response=syslog_config)
        ret = syslog.Syslog(self._global_admin).get_configuration()
        self._global_admin.api.get.assert_called_once_with('/settings/logsSettings/syslogConfig')
        self.assertEqual(ret, syslog_config)

    def test_enable_syslog_default_args(self):
        put_response = 'Success'
        self._init_global_admin(put_response=put_response)
        ret = syslog.Syslog(self._global_admin).enable(self._server)
        self._global_admin.api.put.assert_called_once_with('/settings/logsSettings/syslogConfig', mock.ANY)
        expected_param = self._default_settings()
        actual_param = self._global_admin.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, put_response)

    def test_modify_enabled_syslog(self):
        get_response = munch.Munch()
        put_response = 'Success'
        self._init_global_admin(get_response=get_response, put_response=put_response)
        ret = syslog.Syslog(self._global_admin).modify(self._server, self._port, IPProtocol.UDP, Severity.INFO)
        self._global_admin.api.get.assert_called_once_with('/settings/logsSettings/syslogConfig')
        self._global_admin.api.put.assert_called_once_with('/settings/logsSettings/syslogConfig', mock.ANY)
        expected_param = self._default_settings()
        actual_param = self._global_admin.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, put_response)

    def test_modify_disabled_syslog(self):
        get_response = munch.Munch({'mode': Mode.Disabled})
        self._init_global_admin(get_response=get_response)
        with self.assertRaises(exceptions.CTERAException) as error:
            syslog.Syslog(self._global_admin).modify()
        self._global_admin.api.get.assert_called_once_with('/settings/logsSettings/syslogConfig')
        self.assertEqual('Syslog configuration cannot be modified when disabled', error.exception.message)
        
    def _default_settings(self):
        param = Object()
        param._classname = 'PortalSyslogConfig'  # pylint: disable=protected-access
        param.mode = Mode.Enabled
        param.server = self._server
        param.minSeverity = Severity.INFO
        param.port = self._port
        param.protocol = IPProtocol.UDP
        param.useClientCertificate = False
        return param

    def test_disable_syslog(self):
        put_response = 'Success'
        self._init_global_admin(put_response=put_response)
        ret = syslog.Syslog(self._global_admin).disable()
        self._global_admin.api.put.assert_called_once_with('/settings/logsSettings/syslogConfig/mode', Mode.Disabled)
        self.assertEqual(ret, put_response)
