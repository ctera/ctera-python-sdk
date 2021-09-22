import logging

from ..common import union, parse_base_object_ref, ApplicationBackupSet, PolicyRuleConverter, Object
from ..exception import CTERAException, ObjectNotFoundException
from .base_command import BaseCommand
from . import query
from .enum import Platform


class Templates(BaseCommand):
    """
    Portal Configuration Template APIs
    """

    default = ['name']

    def __init__(self, portal):
        super().__init__(portal)
        self.auto_assign = TemplateAutoAssignPolicy(self._portal)

    def _get_entire_object(self, name):
        try:
            return self._portal.get(f'/deviceTemplates/{name}')
        except CTERAException as error:
            raise CTERAException('Failed to get template', error)

    def get(self, name, include=None):
        """
        Get a Configuration Template

        :param str name: Name of the template
        :param list[str] include: List of fields to retrieve, defaults to ``['name']``
        """
        include = union(include or [], Templates.default)
        include = ['/' + attr for attr in include]
        template = self._portal.get_multi('/deviceTemplates/' + name, include)
        if template.name is None:
            raise ObjectNotFoundException('Could not find server', f'/deviceTemplates/{name}', name=name)
        return template

    def add(self, name, description=None, include_sets=None, exclude_sets=None,
            apps=None, backup_schedule=None, versions=None, scripts=None, cli_commands=None):
        """
        Add a Configuration Template

        :param str name: Name of the template
        :param str,optional description: Template description
        :param list[cterasdk.common.types.FilterBackupSet],optional include_sets: List of backup sets to include
        :param list[cterasdk.common.types.FilterBackupSet],optional exclude_sets: List of backup sets to exclude
        :param list[cterasdk.common.enum.Application],optional apps: List of applications to back up
        :param cterasdk.common.types.TaskSchedule,optional backup_schedule: Backup schedule
        :param list[cterasdk.core.types.PlatformVersion],optional versions: List of platforms and their associated versions.
         Pass `None` to inehrit the default settings from the Global Administration Portal
        :param list[cterasdk.core.types.TemplateScript],optional scripts: Scripts to execute after logon, before or after backup
        :param list[str],optional cli_commands: Template CLI commands to execute
        """
        param = Object()
        param._classname = 'DeviceTemplate'  # pylint: disable=protected-access
        param.name = name
        param.description = description

        self._configure_firmware_settings(param, versions)

        param.deviceSettings = Object()
        param.deviceSettings._classname = 'DeviceTemplateSettings'  # pylint: disable=protected-access

        Templates._configure_backup_settings(param, include_sets, exclude_sets, backup_schedule, apps)
        Templates._add_scripts(param, scripts)
        Templates._add_cli_commands(param, cli_commands)

        logging.getLogger().info('Adding template. %s', {'name': name})
        response = self._portal.add('/deviceTemplates', param)
        logging.getLogger().info('Template added. %s', {'name': name})
        return response

    def _configure_firmware_settings(self, param, versions):
        param.firmwaresSettings = Object()
        param.firmwaresSettings._classname = 'FirmwaresSettings'  # pylint: disable=protected-access

        if versions:
            param.firmwaresSettings.useGlobal = False
            param.firmwaresSettings.firmwares = self._convert_to_template_firmwares(versions)
        else:
            param.firmwaresSettings.useGlobal = True
            param.firmwaresSettings.firmwares = None

    @staticmethod
    def _configure_backup_settings(param, include_sets, exclude_sets, backup_schedule, apps):
        if include_sets or exclude_sets or backup_schedule or apps:
            param.deviceSettings.backup = Object()
            param.deviceSettings.backup._classname = 'BackupTemplate'  # pylint: disable=protected-access
            param.deviceSettings.backup.backupPolicy = Object()
            param.deviceSettings.backup.backupPolicy._classname = 'BackupPolicyTemplate'  # pylint: disable=protected-access
            if include_sets:
                param.deviceSettings.backup.backupPolicy.includeSets = include_sets
            if exclude_sets:
                param.deviceSettings.backup.backupPolicy.excludeSets = exclude_sets
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

    @staticmethod
    def _add_scripts(param, scripts):
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

    @staticmethod
    def _add_cli_commands(param, cli_commands):
        if cli_commands:
            param.deviceSettings.cliCommands = Object()
            param.deviceSettings.cliCommands._classname = 'CliCommandTemplate'  # pylint: disable=protected-access
            param.deviceSettings.cliCommands.cliCommands = cli_commands

    def _convert_to_template_firmwares(self, versions):
        firmwares = {image.name: parse_base_object_ref(image.baseObjectRef) for image in self._portal.firmwares.list_images()}

        template_firmwares = []
        for platform, version in versions:
            base_object_ref = firmwares.get(f'{platform}-{version}')
            if base_object_ref is None:
                raise CTERAException('Could not find firmware version', None, platform=platform, version=version)
            template_firmwares.append(Templates._create_template_firmware(platform, str(base_object_ref)))

        return template_firmwares

    @staticmethod
    def _create_template_firmware(platform, base_object_ref):
        param = Object()
        param._classname = 'TemplateFirmware'  # pylint: disable=protected-access
        param.type = platform
        param.firmware = base_object_ref
        return param

    def by_name(self, names, include=None):
        """
        Get Templates by their names

        :param list[str],optional names: List of names of templates
        :param list[str],optional include: List of fields to retrieve, defaults to ['name']
        :param list[cterasdk.core.query.FilterBuilder],optional filters: List of additional filters, defaults to None

        :return: Iterator for all matching Templates
        :rtype: cterasdk.lib.iterator.Iterator
        """
        filters = [query.FilterBuilder('name').eq(name) for name in names]
        return self.list_templates(include, filters)

    def list_templates(self, include=None, filters=None):
        """
        List Configuration Templates.\n
        To retrieve templates, you must first browse the tenant, using: `GlobalAdmin.portals.browse()`

        :param list[str],optional include: List of fields to retrieve, defaults to ``['name']``
        :param list[],optional filters: List of additional filters, defaults to None
        """
        include = union(include or [], Templates.default)
        builder = query.QueryParamBuilder().include(include)
        if filters:
            for query_filter in filters:
                builder.addFilter(query_filter)
            builder.orFilter((len(filters) > 1))
        param = builder.build()
        return query.iterator(self._portal, '/deviceTemplates', param)

    def delete(self, name):
        """
        Delete a Configuration Template

        :param str name: Name of the template
        """
        logging.getLogger().info('Deleting template. %s', {'name': name})
        response = self._portal.delete(f'/deviceTemplates/{name}')
        logging.getLogger().info('Template deleted. %s', {'name': name})
        return response

    def set_default(self, name, wait=False):
        """
        Set a Configuration Template as the default template

        :param str name: Name of the template
        :param bool,optional wait: Wait for all changes to apply, defaults to `False`
        """
        logging.getLogger().info('Setting default template. %s', {'name': name})
        response = self._portal.execute(f'/deviceTemplates/{name}', 'setAsDefault')
        self.auto_assign.apply_changes(wait=wait)
        logging.getLogger().info('Set default template. %s', {'name': name})
        return response

    def remove_default(self, name, wait=False):
        """
        Set a Configuration Template not to be the default template

        :param str name: Name of the template
        :param bool,optional wait: Wait for all changes to apply, defaults to `False`
        """
        template = self.get(name, include=['isDefault'])
        if template.isDefault:
            logging.getLogger().info('Removing default template. %s', {'name': name})
            response = self._portal.execute('', 'removeDefaultDeviceTemplate')
            logging.getLogger().info('Removed default template. %s', {'name': name})
            self.auto_assign.apply_changes(wait=wait)
            return response
        logging.getLogger().info('Template not set as default. %s', {'name': name})
        return None


class TemplateAutoAssignPolicy(BaseCommand):

    def get_policy(self):
        """
        Get templates auto assignment policy
        """
        return self._portal.execute('', 'getAutoAssignmentRules')

    def set_policy(self, rules, apply_default=None, default=None, apply_changes=True):
        """
        Set templates auto assignment policy

        :param list[cterasdk.common.types.PolicyRule] rules: List of policy rules
        :param bool,optional apply_default: If no match found, apply default template. If not passed, the current config will be kept
        :param str,optional default: Name of a template to assign if no match found. Ignored unless the ``apply_default`` is set to ``True``
        :param bool,optional apply_changes: Apply changes upon update, defaults to ``True``
        """
        templates = {rule.assignment for rule in rules}
        if default:
            templates.add(default)
        templates = list(templates)
        portal_templates = {template.name: template for template in self._portal.templates.by_name(templates, ['baseObjectRef'])}

        not_found = [template for template in templates if template not in portal_templates.keys()]
        if not_found:
            logging.getLogger().error('Could not find one or more templates. %s', {'templates': not_found})
            raise CTERAException('Could not find one or more templates', None, templates=not_found)

        policy = self.get_policy()

        if apply_default is False:
            policy.defaultTemplate = None
        elif apply_default is True and default:
            policy.defaultTemplate = portal_templates.get(default).baseObjectRef

        policy_rules = [PolicyRuleConverter.convert(rule, 'DeviceTemplateAutoAssignmentRule', 'template',
                        portal_templates.get(rule.assignment).baseObjectRef) for rule in rules]
        policy.deviceTemplatesAutoAssignmentRules = policy_rules

        response = self._portal.execute('', 'setAutoAssignmentRules', policy)
        logging.getLogger().info('Set templates auto assignment rules.')

        if apply_changes:
            self.apply_changes(True)

        return response

    def apply_changes(self, wait=False):
        """
        Apply provisioning changes.\n

        :param bool,optional wait: Wait for all changes to apply, defaults to `False`
        """
        task = self._portal.execute('', 'applyAutoAssignmentRules')
        if wait:
            task = self._portal.tasks.wait(task)
        return task
