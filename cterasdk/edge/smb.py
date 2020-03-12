import logging

from ..common import Object
from .enum import Mode, CIFSPacketSigning
from ..exception import CTERAException, InputError
from .base_command import BaseCommand


class SMB(BaseCommand):
    """ Gateway SMB configuration APIs """

    def enable(self):
        """ Enable SMB """
        logging.getLogger().info('Enabling SMB server.')
        self._gateway.put('/config/fileservices/cifs/mode', Mode.Enabled)
        logging.getLogger().info('SMB server enabled.')

    def enable_abe(self):
        """ Enable ABE """
        logging.getLogger().info('Enabling ABE.')
        self._gateway.put('/config/fileservices/cifs/hideUnreadable', True)
        logging.getLogger().info('Access Based Enumeration (ABE) enabled.')

    def disable_abe(self):
        """ Disable ABE """
        logging.getLogger().info('Disabling ABE.')
        self._gateway.put('/config/fileservices/cifs/hideUnreadable', False)
        logging.getLogger().info('Access Based Enumeration (ABE) disabled.')

    def set_packet_signing(self, packet_signing):
        """
        Set Packet signing

        :param cterasdk.edge.enum.CIFSPacketSigning packet_signing: Packet signing type
        """
        self._verify_packet_signing_parameter(packet_signing)
        logging.getLogger().info('Updating SMB packet signing configuration.')
        try:
            self._gateway.put('/config/fileservices/cifs/packetSigning', packet_signing)
            logging.getLogger().info('SMB packet signing configuration updated. %s', {'packet_signing': packet_signing})
        except CTERAException as error:
            logging.getLogger().error('Failed to update SMB packet signing configuration.')
            raise CTERAException('Invalid packet signing co', error)

    def disable(self):
        """ Disble SMB """
        logging.getLogger().info('Disabling SMB server.')
        self._gateway.put('/config/fileservices/cifs/mode', Mode.Disabled)
        logging.getLogger().info('SMB server disabled.')

    def get_configuration(self):
        """
        Get current SMB Configuration

        :return cterasdk.common.object.Object: SMB configuration
        """
        cifs = self._gateway.get('/config/fileservices/cifs')
        obj = Object()
        obj.mode = cifs.mode
        if obj.mode == Mode.Enabled:
            obj.packet_signing = cifs.packetSigning
            obj.idle_disconnect_time = cifs.idleDisconnectTime
            obj.compatibility_mode = cifs.compatibilityMode
            obj.cifs_unix_extensions = cifs.cifsUnixExtensions
            obj.abe_enabled = cifs.hideUnreadable
        return obj

    def modify(
            self,
            packet_signing=None,
            idle_disconnect_time=None,
            compatibility_mode=None,
            unix_extensions=None,
            abe_enabled=None):
        """
        Modify the current SMB Configuration. Parameters that are not passed will not be affected

        :param cterasdk.edge.enum.CIFSPacketSigning packet_signing,optional: Packet signing type
        :param int,optional idle_disconnect_time: Client idle disconnect timeout
        :param bool,optional compatibility_mode: Enable/Disable compatibility mode
        :param bool,optional unix_extensions: Enable/Disable unix extensions
        :param bool,optional abe_enabled: Enable/Disable ABE
        """
        cifs = self._gateway.get('/config/fileservices/cifs')
        if cifs.mode != Mode.Enabled:
            raise CTERAException("SMB must be enabled in order to modify its configuration")
        if packet_signing is not None:
            self._verify_packet_signing_parameter(packet_signing)
            cifs.packetSigning = packet_signing
        if idle_disconnect_time is not None:
            cifs.idleDisconnectTime = idle_disconnect_time
        if compatibility_mode is not None:
            cifs.compatibilityMode = compatibility_mode
        if unix_extensions is not None:
            cifs.cifsUnixExtensions = unix_extensions
        if abe_enabled is not None:
            cifs.hideUnreadable = abe_enabled
        try:
            self._gateway.put('/config/fileservices/cifs', cifs)
            logging.getLogger().info('SMB configuration updated.')
        except CTERAException as error:
            msg = 'Failed to update SMB configuration.'
            logging.getLogger().error(msg)
            raise CTERAException(message=msg, instace=error)

    @staticmethod
    def _verify_packet_signing_parameter(packet_signing):
        options = [v for k, v in CIFSPacketSigning.__dict__.items() if not k.startswith('_')]
        if packet_signing not in options:
            raise InputError('Invalid packet signing option', packet_signing, options)
