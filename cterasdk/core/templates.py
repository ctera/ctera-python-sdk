import logging

from ..common import union, Object
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

    def add(self, name, description=None, include_sets=None, exclude_sets=None):
        """
        Add a Configuration Template

        :param str name: Name of the template
        """
        param = Object()
        param._classname = 'DeviceTemplate'  # pylint: disable=protected-access
        param.name = name
        param.description = description

        param.deviceSettings = Object()
        param.deviceSettings._classname = 'DeviceTemplateSettings'  # pylint: disable=protected-access

        if include_sets or exclude_sets:
            param.deviceSettings.backup = Object()
            param.deviceSettings.backup._classname = 'BackupTemplate'  # pylint: disable=protected-access
            param.deviceSettings.backup.backupPolicy = Object()
            param.deviceSettings.backup.backupPolicy._classname = 'BackupPolicyTemplate'  # pylint: disable=protected-access
            if include_sets:
                param.deviceSettings.backup.backupPolicy.includeSets = include_sets
            if exclude_sets:
                param.deviceSettings.backup.backupPolicy.excludeSets = exclude_sets

        logging.getLogger().info('Adding template. %s', {'name': name})
        response = self._portal.add('/deviceTemplates', param)
        logging.getLogger().info('Template added. %s', {'name': name})
        return response

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
