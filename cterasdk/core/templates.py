import logging

from ..common import union, parse_base_object_ref, ApplicationBackupSet, Object
from ..exception import CTERAException
from .base_command import BaseCommand
from . import query


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
            return self._portal.get('/deviceTemplates/%s' % name)
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
            raise CTERAException('Could not find template', None, name=name)
        return template

    def add(self, name, description=None, include_sets=None, exclude_sets=None, apps=None, backup_schedule=None, versions=None):
        """
        Add a Configuration Template

        :param str name: Name of the template
        :param str description: Template description
        :param list[cterasdk.common.types.FilterBackupSet] include_sets: List of backup sets to include
        :param list[cterasdk.common.types.FilterBackupSet] exclude_sets: List of backup sets to exclude
        :param list[cterasdk.core.enum.Application] apps: List of applications to back up
        :param cterasdk.common.types.TaskSchedule backup_schedule: Backup schedule
        :param list[cterasdk.core.types.PlatformVersion] versions: List of platforms and their associated versions.
        Pass `None` to inehrit the default settings from the Global Administration Portal
        """
        param = Object()
        param._classname = 'DeviceTemplate'  # pylint: disable=protected-access
        param.name = name
        param.description = description

        param.firmwaresSettings = Object()
        param.firmwaresSettings._classname = 'FirmwaresSettings'  # pylint: disable=protected-access

        if versions:
            param.firmwaresSettings.useGlobal = False
            param.firmwaresSettings.firmwares = self._convert_to_template_firmwares(versions)
        else:
            param.firmwaresSettings.useGlobal = True
            param.firmwaresSettings.firmwares = None

        param.deviceSettings = Object()
        param.deviceSettings._classname = 'DeviceTemplateSettings'  # pylint: disable=protected-access

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

        logging.getLogger().info('Adding template. %s', {'name': name})
        response = self._portal.add('/deviceTemplates', param)
        logging.getLogger().info('Template added. %s', {'name': name})
        return response

    def _convert_to_template_firmwares(self, versions):
        firmwares = {image.name: parse_base_object_ref(image.baseObjectRef) for image in self._portal.firmwares.list_images()}

        template_firmwares = []
        for platform, version in versions:
            base_object_ref = firmwares.get('%s-%s' % (platform, version))
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

    def list_templates(self, include=None):
        """
        List Configuration Templates.\n
        To retrieve templates, you must first browse the tenant, using: `GlobalAdmin.portals.browse()`

        :param list[str],optional include: List of fields to retrieve, defaults to ``['name']``
        """
        include = union(include or [], Templates.default)
        param = query.QueryParamBuilder().include(include).build()
        return query.iterator(self._portal, '/deviceTemplates', param)

    def delete(self, name):
        """
        Delete a Configuration Template

        :param str name: Name of the template
        """
        logging.getLogger().info('Deleting template. %s', {'name': name})
        response = self._portal.delete('/deviceTemplates/%s' % name)
        logging.getLogger().info('Template deleted. %s', {'name': name})
        return response

    def set_default(self, name, wait=False):
        """
        Set a Configuration Template as the default template

        :param str name: Name of the template
        :param bool,optional wait: Wait for all changes to apply, defaults to `False`
        """
        logging.getLogger().info('Setting default template. %s', {'name': name})
        response = self._portal.execute('/deviceTemplates/%s' % name, 'setAsDefault')
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

    def apply_changes(self, wait=False):
        """
        Apply provisioning changes.\n

        :param bool,optional wait: Wait for all changes to apply, defaults to `False`
        """
        task = self._portal.execute('', 'applyAutoAssignmentRules')
        if wait:
            task = self._portal.tasks.wait(task)
        return task
