# pylint: disable=protected-access
from unittest import mock

import munch
from cterasdk.common import Object
from cterasdk.core import templates
from cterasdk.core.types import TemplateScript, PlatformVersion
from cterasdk.common.types import ApplicationBackupSet, FileFilterBuilder, FilterBackupSet, BackupScheduleBuilder, \
                                  TimeRange, BackupScheduleBuilder, SoftwareUpdatePolicyBuilder  # noqa: E402, F401
from cterasdk.common.enum import DayOfWeek, Application
from cterasdk.common.types import ConsentPage
from cterasdk.core.enum import Platform, EnvironmentVariables
from cterasdk import exceptions
from tests.ut import base_core


class TestCoreTemplates(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._name = 'Template'
        self._classname = 'DeviceTemplate'
        self._description = 'description'

    def test_get_template_default_attrs(self):
        get_multi_response = self._get_template_object(name=self._name)
        self._init_global_admin(get_multi_response=get_multi_response)
        ret = templates.Templates(self._global_admin).get(self._name)
        self._global_admin.api.get_multi.assert_called_once_with(f'/deviceTemplates/{self._name}', mock.ANY)
        expected_include = ['/' + attr for attr in templates.Templates.default]
        actual_include = self._global_admin.api.get_multi.call_args[0][1]
        self.assertEqual(len(expected_include), len(actual_include))
        for attr in expected_include:
            self.assertIn(attr, actual_include)
        self.assertEqual(ret.name, self._name)

    def test_get_template_not_found(self):
        get_multi_response = self._get_template_object(name=None)
        self._init_global_admin(get_multi_response=get_multi_response)
        with self.assertRaises(exceptions.ObjectNotFoundException) as error:
            templates.Templates(self._global_admin).get(self._name)
        self._global_admin.api.get_multi.assert_called_once_with(f'/deviceTemplates/{self._groupname}', mock.ANY)
        expected_include = ['/' + attr for attr in templates.Templates.default]
        actual_include = self._global_admin.api.get_multi.call_args[0][1]
        self.assertEqual(len(expected_include), len(actual_include))
        for attr in expected_include:
            self.assertIn(attr, actual_include)
        self.assertEqual('Could not find template', error.exception.message)

    def test_list_templates_default_attrs(self):
        with mock.patch("cterasdk.core.templates.query.iterator") as query_iterator_mock:
            templates.Templates(self._global_admin).list_templates()
            query_iterator_mock.assert_called_once_with(self._global_admin, '/deviceTemplates', mock.ANY)
            expected_query_params = base_core.BaseCoreTest._create_query_params(include=templates.Templates.default,
                                                                                start_from=0, count_limit=50)
            actual_query_params = query_iterator_mock.call_args[0][2]
            self._assert_equal_objects(actual_query_params, expected_query_params)

    def test_delete_template(self):
        delete_response = 'Success'
        self._init_global_admin(delete_response=delete_response)
        ret = templates.Templates(self._global_admin).delete(self._name)
        self._global_admin.api.delete.assert_called_once_with(f'/deviceTemplates/{self._name}')
        self.assertEqual(ret, delete_response)

    def test_set_default_template_no_wait(self):
        execute_response = 'Success'
        self._init_global_admin(execute_response=execute_response)
        ret = templates.Templates(self._global_admin).set_default(self._name)
        self._global_admin.api.execute.assert_has_calls([
            mock.call(f'/deviceTemplates/{self._name}', 'setAsDefault'),
            mock.call('', 'applyAutoAssignmentRules')
        ])
        self.assertEqual(ret, execute_response)

    def test_remove_default_template_no_wait(self):
        execute_response = 'Success'
        get_multi_response = self._get_template_object(name=self._name, isDefault=True)
        self._init_global_admin(get_multi_response=get_multi_response, execute_response=execute_response)
        ret = templates.Templates(self._global_admin).remove_default(self._name)
        self._global_admin.api.get_multi.assert_called_once_with(f'/deviceTemplates/{self._name}', mock.ANY)
        self._global_admin.api.execute.assert_has_calls([
            mock.call('', 'removeDefaultDeviceTemplate'),
            mock.call('', 'applyAutoAssignmentRules')
        ])
        self.assertEqual(ret, execute_response)

    def test_add_template_default_args(self):
        add_response = 'Success'
        self._init_global_admin(add_response=add_response)
        parameters = TestCoreTemplates._template_parameters()
        ret = templates.Templates(self._global_admin).add(self._name, self._description, include_sets=parameters.include_sets, exclude_sets=None,
                                                          apps=parameters.apps, backup_schedule=parameters.backup_schedule,
                                                          update_settings=parameters.update_settings, scripts=parameters.scripts, cli_commands=parameters.cli_commands,
                                                          consent_page=parameters.consent_page)
        self._global_admin.api.add.assert_called_once_with(f'/deviceTemplates', mock.ANY)
        expected_param = self._create_template_param(parameters.include_sets, parameters.backup_schedule, parameters.apps, parameters.scripts,
                                                     parameters.cli_commands, parameters.update_settings, parameters.consent_page)
        actual_param = self._global_admin.api.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, add_response)

    @staticmethod
    def _template_parameters():
        """Include all 'pptx', 'xlsx' and 'docx' file types for all users"""
        docs = FileFilterBuilder.extensions().include(['pptx', 'xlsx', 'docx']).build()
        include_sets = FilterBackupSet('Documents', filter_rules=[docs], template_dirs=[EnvironmentVariables.ALLUSERSPROFILE])

        """Schedule backup for a specific time"""
        time_range = TimeRange().start('07:00:00').days(DayOfWeek.Weekdays).build()  # 7am, on weekdays
        backup_schedule = BackupScheduleBuilder.window(time_range)

        """Backup applications"""
        apps = Application.All  # back up all applications

        """Configure software update schedule"""
        schedule = TimeRange().start('01:00:00').end('02:00:00').days(DayOfWeek.Weekdays).build()
        update_settings = SoftwareUpdatePolicyBuilder().download_and_install(True).reboot_after_update(True).schedule(schedule).build()

        """Configure Scripts"""
        scripts = [
            TemplateScript.windows().after_logon('echo Current directory: %cd%'),
            TemplateScript.linux().before_backup('./mysqldump -u admin website > /mnt/backup/backup.sql'),
            TemplateScript.linux().after_backup('rm /mnt/backup/backup.sql')
        ]

        """Configure CLI Commands"""
        cli_commands = [
            'set /config/agent/stubs/deleteFilesOfCachedFolderOnDisable false',
            'add /config/agent/stubs/allowedExplorerExtensions url'
        ]

        """Configure Consent Page"""
        consent_page = ConsentPage('the header of your consent page', 'the body of your consent page')
        
        return munch.Munch({
            'include_sets': include_sets,
            'backup_schedule': backup_schedule,
            'apps': apps,
            'scripts': scripts,
            'cli_commands': cli_commands,
            'update_settings': update_settings,
            'consent_page': consent_page
        })

    def _create_template_param(self, include_sets=None, backup_schedule=None, apps=None,
                        scripts=None, cli_commands=None, update_settings=None, consent_page=None):
        param = Object()
        param._classname = self._classname  # pylint: disable=protected-access
        param.name = self._name
        param.description = self._description
        param.firmwaresSettings = Object()
        param.firmwaresSettings._classname = 'FirmwaresSettings'  # pylint: disable=protected-access
        param.firmwaresSettings.useGlobal = True
        param.firmwaresSettings.firmwares = None
        param.deviceSettings = Object()
        param.deviceSettings._classname = 'DeviceTemplateSettings'  # pylint: disable=protected-access
        if include_sets or backup_schedule or apps:
            param.deviceSettings.backup = Object()
            param.deviceSettings.backup._classname = 'BackupTemplate'  # pylint: disable=protected-access
            param.deviceSettings.backup.backupPolicy = Object()
            param.deviceSettings.backup.backupPolicy._classname = 'BackupPolicyTemplate'  # pylint: disable=protected-access
            if include_sets:
                param.deviceSettings.backup.backupPolicy.includeSets = include_sets
            if backup_schedule:
                param.deviceSettings.backup.scheduleTopic = Object()
                param.deviceSettings.backup.scheduleTopic._classname = 'ScheduleTopic'  # pylint: disable=protected-access
                param.deviceSettings.backup.scheduleTopic.overrideTemplate = True
                param.deviceSettings.backup.scheduleTopic.schedule = backup_schedule
            if apps:
                param.deviceSettings.backup.applicationsTopic = Object()
                param.deviceSettings.backup.applicationsTopic._classname = 'ApplicationsTopic'  # pylint: disable=protected-access
                param.deviceSettings.backup.applicationsTopic.overrideTemplate = True
                param.deviceSettings.backup.applicationsTopic.includeApps = ApplicationBackupSet(apps)
            if scripts:
                param.deviceSettings.scripts = Object()
                param.deviceSettings.scripts._classname = 'ScriptTemplates'  # pylint: disable=protected-access
                for script in scripts:
                    server_object = script.to_server_object()
                    if script.platform == Platform.Windows:
                        param.deviceSettings.scripts.windowsScripts = server_object
                    if script.platform == Platform.Linux:
                        param.deviceSettings.scripts.linuxScripts = server_object
                    if script.platform == Platform.OSX:
                        param.deviceSettings.scripts.macScripts = server_object
            if cli_commands:
                param.deviceSettings.cliCommands = Object()
                param.deviceSettings.cliCommands._classname = 'CliCommandTemplate'  # pylint: disable=protected-access
                param.deviceSettings.cliCommands.cliCommands = cli_commands
            if update_settings:
                param.deviceSettings.softwareUpdates = Object()
                param.deviceSettings.softwareUpdates._classname = 'SoftwareUpdatesTopic'  # pylint: disable=protected-access
                param.deviceSettings.softwareUpdates.overrideTemplate = False
                param.deviceSettings.softwareUpdates.softwareUpdates = update_settings
            if consent_page:
                param.deviceSettings.consentPage = Object()
                param.deviceSettings.consentPage._classname = 'ConsentPageTopic'  # pylint: disable=protected-access
                param.deviceSettings.consentPage.enabled = True
                param.deviceSettings.consentPage.consentPageHeader = consent_page.header
                param.deviceSettings.consentPage.consentPageBody = consent_page.body
        return param

    def _get_template_object(self, **kwargs):
        template_object = Object()
        template_object._classname = self._classname  # pylint: disable=protected-access
        for key, value in kwargs.items():
            setattr(template_object, key, value)
        return template_object
