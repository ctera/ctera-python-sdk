import logging
from .base_command import BaseCommand
from .enum import Reports
from ..exceptions import InputError


class Reports(BaseCommand):
    """
    Reports APIs
    """
    def storage(self):
        """
        Retrieve the portals statistics report.\n
        To retrieve this report, you must first browse the Global Administration Portal, using: `GlobalAdmin.portals.browse_global_admin()`
        """
        return self._get_report(Reports.Storage)

    def portals(self):
        """
        Retrieve the storage statistics report.\n
        To retrieve this report, you must first browse the Global Administration Portal, using: `GlobalAdmin.portals.browse_global_admin()`
        """
        return self._get_report(Reports.Portals)

    def folders(self):
        """
        Retrieve the cloud folders statistics report.\n
        To retrieve this report, you must first browse the Virtual Portal that contains the report, using: `GlobalAdmin.portals.browse()`
        """
        return self._get_report(Reports.Folders)

    def folder_groups(self):
        """
        Retrieve the folder groups statistics report.\n
        To retrieve this report, you must first browse the Virtual Portal that contains the report, using: `GlobalAdmin.portals.browse()`
        """
        return self._get_report(Reports.FolderGroups)
    
    def generate(self, name):
        """
        Generate a CTERA Portal Report

        :param cterasdk.core.enum.reports report: Report
        """
        options = {k: v for k,v in Reports.__dict__.items() if not k.startswith('_')}
        report = options.get(name, None)
        if report is None:
            raise InputError('Invalid report type.', name, options.keys())
        logging.gerLogger().info('Running Portal Report. %s', {'name': name})
        self._core.execute('', 'generateReport', report)

    def _get_report(self, report_name):
        return self._core.api.get(f'/reports/{report_name}')
