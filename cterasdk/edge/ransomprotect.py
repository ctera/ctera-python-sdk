import logging
from .base_command import BaseCommand
from ..exception import CTERAException


class RansomProtect(BaseCommand):
    """
    Ransomware Protect APIs
    """

    def get_configuration(self):
        """
        Get the current Ransomware Protect configuration

        :return cterasdk.common.object.Object:
        """
        return self._gateway.get('/config/ransomProtect/')

    def enable(self):
        """ Enable Ransomware Protect service """
        logging.getLogger().info('Enabling Ransomware Protect.')
        self._gateway.put('/config/ransomProtect/enabled', True)
        logging.getLogger().info('Ransomware Protect Enabled.')

    def disable(self):
        """ Enable Ransomware Protect service """
        logging.getLogger().info('Disabling Ransomware Protect.')
        self._gateway.put('/config/ransomProtect/enabled', False)
        logging.getLogger().info('Ransomware Protect disabled.')

    def is_disabled(self):
        """ Check if the Ransomware Protect is disabled """
        return self._gateway.get('/config/ransomProtect/enabled') is not True

    def modify(
            self,
            should_block_user=None,
            min_num_files=None,
            detection_int=None):
        """
        Modify the Ransomware Protect Configuration. Parameters that are not passed will not be affected

        :param bool,optional should_block_user: Enable/Disable Block Users
        :param int,optional min_num_files: Set the number of detection threshold of suspicious events
        :param int,optional detection_int: Set the number of seconds for detection interval

        """
        config = self.get_configuration()
        if not config.enabled:
            raise CTERAException('Ransomware Protect must be enabled in order to modify its configuration')
        if should_block_user is not None:
            config.shouldBlockUser = should_block_user
        if min_num_files is not None:
            config.minimalNumOfFilesForPositiveDetection = min_num_files
        if detection_int is not None:
            config.detectionInterval = detection_int
        self._gateway.put('/config/ransomProtect/', config)
