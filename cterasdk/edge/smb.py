import logging

from ..common import Object
from .enum import Mode, CIFSPacketSigning, SMBProtocol
from ..exceptions import CTERAException, InputError
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


class SMB(BaseCommand):
    """ Edge Filer SMB configuration APIs """

    def enable(self):
        """ Enable SMB """
        logger.info('Enabling SMB server.')
        self._edge.api.put('/config/fileservices/cifs/mode', Mode.Enabled)
        logger.info('SMB server enabled.')

    def enable_abe(self):
        """ Enable ABE """
        logger.info('Enabling ABE.')
        self._edge.api.put('/config/fileservices/cifs/hideUnreadable', True)
        logger.info('Access Based Enumeration (ABE) enabled.')

    def disable_abe(self):
        """ Disable ABE """
        logger.info('Disabling ABE.')
        self._edge.api.put('/config/fileservices/cifs/hideUnreadable', False)
        logger.info('Access Based Enumeration (ABE) disabled.')

    def set_packet_signing(self, packet_signing):
        """
        Set Packet signing

        :param cterasdk.edge.enum.CIFSPacketSigning packet_signing: Packet signing type
        """
        self._verify_packet_signing_parameter(packet_signing)
        logger.info('Updating SMB packet signing configuration.')
        try:
            self._edge.api.put('/config/fileservices/cifs/packetSigning', packet_signing)
            logger.info('SMB packet signing configuration updated: %s', packet_signing)
        except CTERAException as error:
            logger.error('Invalid SMB packet signing configuration: %s', packet_signing)
            raise CTERAException(f'Invalid packet SMB signing configuration: {packet_signing}') from error

    def disable(self):
        """ Disable SMB """
        logger.info('Disabling SMB server.')
        self._edge.api.put('/config/fileservices/cifs/mode', Mode.Disabled)
        logger.info('SMB server disabled.')

    def restart(self):
        self.disable()
        self.enable()

    def get_configuration(self):
        """
        Get current SMB Configuration

        :return cterasdk.common.object.Object: SMB configuration
        """
        cifs = self._edge.api.get('/config/fileservices/cifs')
        obj = Object()
        obj.mode = cifs.mode
        if obj.mode == Mode.Enabled:
            obj.packet_signing = cifs.packetSigning
            obj.idle_disconnect_time = cifs.idleDisconnectTime
            obj.compatibility_mode = cifs.compatibilityMode
            obj.cifs_unix_extensions = cifs.cifsUnixExtensions
            obj.abe_enabled = cifs.hideUnreadable
            obj.min_client_protocol = cifs.minClientProtocol
            obj.max_client_protocol = cifs.maxClientProtocol
            obj.min_server_protocol = cifs.minServerProtocol
            obj.max_server_protocol = cifs.maxServerProtocol
        return obj

    def modify(
            self,
            packet_signing=None,
            idle_disconnect_time=None,
            compatibility_mode=None,
            unix_extensions=None,
            abe_enabled=None,
            min_client_protocol=None,
            max_client_protocol=None,
            min_server_protocol=None,
            max_server_protocol=None):
        """
        Modify the current SMB Configuration. Parameters that are not passed will not be affected

        :param cterasdk.edge.enum.CIFSPacketSigning packet_signing,optional: Packet signing type
        :param int,optional idle_disconnect_time: Client idle disconnect timeout
        :param bool,optional compatibility_mode: Enable/Disable compatibility mode
        :param bool,optional unix_extensions: Enable/Disable unix extensions
        :param bool,optional abe_enabled: Enable/Disable ABE
        :param cterasdk.edge.enum.SMBProtocol,optional min_client_protocol: Minimum client protocol version
        :param cterasdk.edge.enum.SMBProtocol,optional max_client_protocol: Maximum client protocol version
        :param cterasdk.edge.enum.SMBProtocol,optional min_server_protocol: Minimum server protocol version
        :param cterasdk.edge.enum.SMBProtocol,optional max_server_protocol: Maximum server protocol version
        """
        cifs = self._edge.api.get('/config/fileservices/cifs')
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
        if min_client_protocol is not None:
            self._verify_smb_protocol_version_parameter(min_client_protocol)
            cifs.minClientProtocol = min_client_protocol
        if max_client_protocol is not None:
            self._verify_smb_protocol_version_parameter(max_client_protocol)
            cifs.maxClientProtocol = max_client_protocol
        if min_server_protocol is not None:
            self._verify_smb_protocol_version_parameter(min_server_protocol)
            cifs.minServerProtocol = min_server_protocol
        if max_server_protocol is not None:
            self._verify_smb_protocol_version_parameter(max_server_protocol)
            cifs.maxServerProtocol = max_server_protocol
        try:
            self._edge.api.put('/config/fileservices/cifs', cifs)
            logger.info('SMB configuration updated.')
        except CTERAException as error:
            message = "An error occurred while trying to modify the SMB server's configuration."
            logger.error(message)
            raise CTERAException(message) from error

    @staticmethod
    def _verify_smb_protocol_version_parameter(smb_protocol_version):
        options = [v for k, v in SMBProtocol.__dict__.items() if not k.startswith('_')]
        if smb_protocol_version not in options:
            raise InputError('Invalid SMB protocol version', smb_protocol_version, options)

    @staticmethod
    def _verify_packet_signing_parameter(packet_signing):
        options = [v for k, v in CIFSPacketSigning.__dict__.items() if not k.startswith('_')]
        if packet_signing not in options:
            raise InputError('Invalid packet signing option', packet_signing, options)
