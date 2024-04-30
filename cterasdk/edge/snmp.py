import logging

from ..exceptions import CTERAException
from ..common import Object
from . import enum
from .base_command import BaseCommand


class SNMP(BaseCommand):
    """ Edge Filer SNMP Configuration APIs """

    def is_enabled(self):
        """
        Check if SNMP is enabled

        :return: True is SNMP is enabled, else False
        :rtype: bool
        """
        return self._edge.api.get('/config/snmp/mode') == enum.Mode.Enabled

    def enable(self, port=161, community_str=None, username=None, auth_password=None, privacy_password=None):
        """
        Enable SNMP

        :param int,optional port: SNMP server port, defaults to 161
        :param str,optional community_str: SNMPv2c community string
        :param str,optional username: SNMPv3 username
        :param str,optional auth_password: SNMPv3 authentication password
        :param str,optional privacy_password: SNMPv3 privacy password
        """
        param = Object()
        param.mode = enum.Mode.Enabled
        param.port = port
        param.readCommunity = community_str
        if username is not None and auth_password is not None and privacy_password is not None:
            param.snmpV3 = Object()
            param.snmpV3.mode = enum.Mode.Enabled
            param.snmpV3.username = username
            param.snmpV3.authenticationPassword = auth_password
            param.snmpV3.privacyPassword = privacy_password

        logging.getLogger('cterasdk.edge').info("Enabling SNMP.")
        self._edge.api.put('/config/snmp', param)
        logging.getLogger('cterasdk.edge').info("Enabled SNMP.")

    def disable(self):
        """ Disable SNMP """
        logging.getLogger('cterasdk.edge').info("Disabling SNMP.")
        self._edge.api.put('/config/snmp/mode', enum.Mode.Disabled)
        logging.getLogger('cterasdk.edge').info("Disabled SNMP.")

    def get_configuration(self):
        return self._edge.api.get('/config/snmp')

    def modify(self, port=None, community_str=None, username=None, auth_password=None, privacy_password=None):
        """
        Modify current SNMP configuration. Only configurations that are not `None` will be changed. SNMP must be enabled

        :param int,optional port: SNMP server port, defaults to 161
        :param str,optional community_str: SNMPv2c community string
        :param str,optional username: SNMPv3 username
        :param str,optional auth_password: SNMPv3 authentication password
        :param str,optional privacy_password: SNMPv3 privacy password
        """
        current_config = self.get_configuration()
        if current_config.mode == enum.Mode.Disabled:
            raise CTERAException("SNMP configuration cannot be modified when disabled")
        if port:
            current_config.port = port
        if community_str:
            current_config.readCommunity = community_str
        if username is not None and auth_password is not None and privacy_password is not None:
            current_config.snmpV3 = Object()
            current_config.snmpV3.mode = enum.Mode.Enabled
            current_config.snmpV3.username = username
            current_config.snmpV3.authenticationPassword = auth_password
            current_config.snmpV3.privacyPassword = privacy_password

        logging.getLogger('cterasdk.edge').info("Updating SNMP configuration.")
        self._edge.api.put('/config/snmp', current_config)
        logging.getLogger('cterasdk.edge').info("SNMP configured.")
