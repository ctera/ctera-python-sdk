from unittest import mock

from cterasdk import toxmlstr
from cterasdk.core import setup
from cterasdk.core.enum import ServerMode, SlaveAuthenticaionMethod, SetupWizardStage, SetupWizardStatus
from cterasdk.common import Object
from tests.ut.core.admin import base_admin


class TestCoreSetup(base_admin.BaseCoreTest):  # pylint: disable=too-many-instance-attributes

    def setUp(self):
        super().setUp()
        self._master_ipaddr = '8.8.8.8'
        self._master_secret = 'password'
        self._admin_username = 'admin'
        self._admin_email = 'admin@ctera.com'
        self._admin_first_name = 'Service'
        self._admin_last_name = 'Account'
        self._admin_password = 'password'
        self._domain = 'ctera.me'
        self._replicate_from = 'server1'

    def test_init_master(self):
        self.patch_call("time.sleep")
        self._init_setup()
        self._global_admin.ctera.get = mock.MagicMock(side_effect=[
            TestCoreSetup._generate_status_response(SetupWizardStage.Server, SetupWizardStatus.NA, ''),
            TestCoreSetup._generate_status_response(SetupWizardStage.Portal, SetupWizardStatus.NA, ''),
            TestCoreSetup._generate_status_response(SetupWizardStage.Finish, SetupWizardStatus.NA, '')
        ])
        mock_startup_wait = self.patch_call("cterasdk.core.startup.Startup.wait")

        setup.Setup(self._global_admin).init_master(self._admin_username, self._admin_email,
                                                    self._admin_first_name, self._admin_last_name, self._admin_password, self._domain)

        setup_status_url = '/setup/status'
        self._global_admin.ctera.get.assert_has_calls(
            [
                mock.call(setup_status_url),
                mock.call(setup_status_url),
                mock.call(setup_status_url)
            ]
        )
        self._global_admin.ctera.execute.assert_called_once_with('/public', 'init', mock.ANY)
        expected_param = self._get_init_portal_param()
        actual_param = self._global_admin.ctera.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

        params = TestCoreSetup._get_init_server_params(ServerMode.Master)
        expected_params = TestCoreSetup._get_form_data(params)
        actual_param = TestCoreSetup._format_actual_parameters_to_dict(self._global_admin.ctera.multipart.call_args[0][1])
        self._global_admin.ctera.multipart.assert_called_once_with('/setup', mock.ANY)
        for key in actual_param.keys():  # pylint: disable=consider-using-dict-items, consider-iterating-dictionary
            self._assert_equal_objects(actual_param[key], expected_params[key])
        mock_startup_wait.assert_called_once()

    @staticmethod
    def _format_actual_parameters_to_dict(actual_param):
        d = {}
        for multi_dict, content_type, value in actual_param.data._fields:  # pylint: disable=protected-access, unused-variable
            d[multi_dict['name']] = value
        return d

    def test_init_master_already_finished(self):
        self._init_setup()
        self._global_admin.ctera.get = mock.MagicMock(side_effect=[
            TestCoreSetup._generate_status_response(SetupWizardStage.Finish, SetupWizardStatus.NA, '')
        ])
        mock_startup_wait = self.patch_call("cterasdk.core.startup.Startup.wait")

        setup.Setup(self._global_admin).init_master(self._admin_username, self._admin_email,
                                                    self._admin_first_name, self._admin_last_name, self._admin_password, self._domain)
        self._global_admin.ctera.get.assert_has_calls(
            [
                mock.call('/setup/status')
            ]
        )
        mock_startup_wait.assert_called_once()

    def test_init_application_server_success_password(self):
        self._test_init_application_server_success(SlaveAuthenticaionMethod.Password)

    def test_init_application_server_success_pk(self):
        self._test_init_application_server_success(SlaveAuthenticaionMethod.PrivateKey)

    def _test_init_application_server_success(self, authentication_method):
        self.patch_call("time.sleep")
        self._init_setup()
        self._global_admin.ctera.get = mock.MagicMock(side_effect=[
            TestCoreSetup._generate_status_response(SetupWizardStage.Server, SetupWizardStatus.NA, ''),
            TestCoreSetup._generate_status_response(SetupWizardStage.Finish, SetupWizardStatus.NA, '')
        ])
        execute_side_effect = TestCoreSetup._create_init_slave_execute_function(authentication_method)
        self._global_admin.ctera.execute = mock.MagicMock(side_effect=execute_side_effect)
        mock_startup_wait = self.patch_call("cterasdk.core.startup.Startup.wait")

        setup.Setup(self._global_admin).init_application_server(self._master_ipaddr, self._master_secret)

        setup_status_url = '/setup/status'
        self._global_admin.ctera.get.assert_has_calls(
            [
                mock.call(setup_status_url),
                mock.call(setup_status_url)
            ]
        )
        self._global_admin.ctera.execute.assert_has_calls(
            [
                mock.call('/setup/authenticaionMethod',
                          'askMasterForSlaveAuthenticaionMethod', self._master_ipaddr)
            ]
        )

        params = TestCoreSetup._get_init_server_params(ServerMode.Slave, authentication_method, self._master_ipaddr, self._master_secret)
        expected_params = TestCoreSetup._get_form_data(params)
        actual_param = TestCoreSetup._format_actual_parameters_to_dict(self._global_admin.ctera.multipart.call_args[0][1])
        self._global_admin.ctera.multipart.assert_called_once_with('/setup', mock.ANY)
        for key in actual_param.keys():  # pylint: disable=consider-using-dict-items, consider-iterating-dictionary
            self._assert_equal_objects(actual_param[key], expected_params[key])
        mock_startup_wait.assert_called_once()

    def _get_init_portal_param(self):
        params = Object()
        params._classname = 'InitParams'  # pylint: disable=protected-access

        params.admin = Object()
        params.admin._classname = 'PortalAdmin'  # pylint: disable=protected-access
        params.admin.name = self._admin_username
        params.admin.email = self._admin_email
        params.admin.firstName = self._admin_first_name
        params.admin.lastName = self._admin_last_name
        params.admin.password = self._admin_password

        params.settings = TestCoreSetup.default_settings()
        params.settings.dnsSuffix = self._domain
        return params

    @staticmethod
    def default_settings():
        settings = Object()
        settings._classname = 'SystemSettings'  # pylint: disable=protected-access
        settings.smtpSettings = Object()
        settings.smtpSettings._classname = 'SMTPSettings'  # pylint: disable=protected-access
        settings.smtpSettings.smtpHost = 'your.mail.server'
        settings.smtpSettings.smtpPort = 25
        settings.smtpSettings.enableTls = False

        settings.defaultPortalSettings = Object()
        settings.defaultPortalSettings._classname = 'PortalSettings'  # pylint: disable=protected-access
        settings.defaultPortalSettings.mailSettings = Object()
        settings.defaultPortalSettings.mailSettings._classname = 'MailSettings'  # pylint: disable=protected-access
        settings.defaultPortalSettings.mailSettings.sender = 'no-reply@your.domain'
        return settings

    @staticmethod
    def _create_init_slave_execute_function(authentication_method):
        def _get_init_slave_execute_function(path, name, param, use_file_url=False):
            # pylint: disable=unused-argument
            if name == 'askMasterForSlaveAuthenticaionMethod':
                return authentication_method
            return None
        return _get_init_slave_execute_function

    @staticmethod
    def _generate_status_response(wizard, currentWizardProgress, description):
        param = Object()
        param.wizard = wizard
        param.currentWizardProgress = currentWizardProgress
        param.description = description
        return param

    @staticmethod
    def _get_form_data(params):
        form_data = {'inputXml': toxmlstr(params).decode('utf-8'), 'serverMode': params.serverMode}
        if params.serverMode == ServerMode.Slave:
            form_data['masterIpAddr'] = params.slaveSettings.masterIpAddr
        return form_data

    @staticmethod
    def _get_init_server_params(mode, authentication_method=None, master_ipaddr=None, master_secret=None):
        params = Object()
        params._classname = 'InitServerParams'  # pylint: disable=protected-access
        params.serverMode = mode
        if mode == ServerMode.Slave:
            params.slaveSettings = Object()
            params.slaveSettings._classname = 'SlaveServerSettings'  # pylint: disable=protected-access
            if master_ipaddr:
                params.slaveSettings.masterIpAddr = master_ipaddr
            if authentication_method == SlaveAuthenticaionMethod.Password:
                params.slaveSettings.masterPassword = master_secret
            elif authentication_method == SlaveAuthenticaionMethod.PrivateKey:
                params.slaveSettings.masterKey = master_secret
        return params
