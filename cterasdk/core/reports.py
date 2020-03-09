from .base_command import BaseCommand


class Reports(BaseCommand):
    """
    Reports APIs
    """
    def storage(self):
        """
        Retrieve the portals statistics report.\n
        To retrieve this report, you must first browse the Global Administration Portal, using: `GlobalAdmin.portals.browse_global_admin()`
        """
        return self._get_report('storageLocationsStatisticsReport')

    def portals(self):
        """
        Retrieve the storage statistics report.\n
        To retrieve this report, you must first browse the Global Administration Portal, using: `GlobalAdmin.portals.browse_global_admin()`
        """
        return self._get_report('portalsStatisticsReport')

    def folders(self):
        """
        Retrieve the cloud folders statistics report.\n
        To retrieve this report, you must first browse the Virtual Portal that contains the report, using: `GlobalAdmin.portals.browse()`
        """
        return self._get_report('foldersStatisticsReport')

    def folder_groups(self):
        """
        Retrieve the folder groups statistics report.\n
        To retrieve this report, you must first browse the Virtual Portal that contains the report, using: `GlobalAdmin.portals.browse()`
        """
        return self._get_report('folderGroupsStatisticsReport')

    def _get_report(self, report_name):
        return self._portal.get('/reports/%s' % report_name)
