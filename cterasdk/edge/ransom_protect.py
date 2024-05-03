import logging
from .base_command import BaseCommand
from . import query
from ..exceptions import CTERAException


class RansomProtect(BaseCommand):
    """
    Ransomware Protect APIs
    """

    def get_configuration(self):
        """
        Get Ransom Protect Configuration

        :return cterasdk.common.object.Object: Configuration
        """
        return self._edge.api.get('/config/ransomProtect/')

    def enable(self):
        """Enable Ransom Protect service"""
        logging.getLogger('cterasdk.edge').info('Enabling Ransom Protect.')
        self._edge.api.put('/config/ransomProtect/enabled', True)
        logging.getLogger('cterasdk.edge').info('Ransom Protect enabled.')

    def disable(self):
        """Enable Ransom Protect service"""
        logging.getLogger('cterasdk.edge').info('Disabling Ransom Protect.')
        self._edge.api.put('/config/ransomProtect/enabled', False)
        logging.getLogger('cterasdk.edge').info('Ransom Protect disabled.')

    def is_disabled(self):
        """Check if Ransom Protect is disabled"""
        return self._edge.api.get('/config/ransomProtect/enabled') is not True

    def modify(self, block_users=None, detection_threshold=None, detection_interval=None):
        """
        Modify Ransom Protect Configuration.

        :param bool,optional block_users: Enable/Disable Block Users
        :param int,optional detection_threshold: Detection threshold (number of events)
        :param int,optional detection_interval: Detection interval (seconds)
        """
        param = self.get_configuration()
        if not param.enabled:
            raise CTERAException('Ransom Protect must be enabled to modify its configuration')
        if block_users is not None:
            param.shouldBlockUser = block_users
        if detection_threshold is not None:
            param.minimalNumOfFilesForPositiveDetection = detection_threshold
        if detection_interval is not None:
            param.detectionInterval = detection_interval
        self._edge.api.put('/config/ransomProtect/', param)

    def incidents(self):
        """
        List Ransomware Incidents

        :return list[cterasdk.common.object.Object]: List of incidents
        """
        return self._edge.api.execute('/proc/rpsrv', 'getListOfIncidents')

    def details(self, incident):
        """
        Retrieve Ransomware Incident Details

        :param int incident: Incident identifier, or an incident object
        """
        param = query.QueryParamBuilder()
        param.put('incidentId', incident if isinstance(incident, int) else incident.incident_id)
        return query.iterator(self._edge, '/proc/rpsrv', param.build(), 'getIncidentDetails')
