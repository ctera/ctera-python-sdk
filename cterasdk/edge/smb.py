import logging

from .enum import Mode, CIFSPacketSigning
from ..exception import CTERAException, InputError
from .base_command import BaseCommand


class SMB(BaseCommand):

    def enable(self):
        logging.getLogger().info('Enabling SMB server.')
        self._gateway.put('/config/fileservices/cifs/mode', Mode.Enabled)
        logging.getLogger().info('SMB server enabled.')

    def enable_abe(self):
        logging.getLogger().info('Enabling ABE.')
        self._gateway.put('/config/fileservices/cifs/hideUnreadable', True)
        logging.getLogger().info('Access Based Enumeration (ABE) enabled.')

    def disable_abe(self):
        logging.getLogger().info('Disabling ABE.')
        self._gateway.put('/config/fileservices/cifs/hideUnreadable', False)
        logging.getLogger().info('Access Based Enumeration (ABE) disabled.')

    def set_packet_signing(self, packet_signing):
        options = [v for k, v in CIFSPacketSigning.__dict__.items() if not k.startswith('_')]
        if packet_signing not in options:
            raise InputError('Invalid packet signing option', packet_signing, options)
        logging.getLogger().info('Updating SMB packet signing configuration.')
        try:
            self._gateway.put('/config/fileservices/cifs/packetSigning', packet_signing)
            logging.getLogger().info('SMB packet signing configuration updated. %s', {'packet_signing': packet_signing})
        except CTERAException as error:
            logging.getLogger().error('Failed to update SMB packet signing configuration.')
            raise CTERAException('Invalid packet signing co', error)

    def disable(self):
        logging.getLogger().info('Disabling SMB server.')
        self._gateway.put('/config/fileservices/cifs/mode', Mode.Disabled)
        logging.getLogger().info('SMB server disabled.')
