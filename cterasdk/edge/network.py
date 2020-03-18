import logging

from .enum import Mode
from . import taskmgr as TaskManager
from ..common import Object
from .base_command import BaseCommand


class Network(BaseCommand):
    """ Gateway Network configuration APIs """

    def get_status(self):
        """
        Retrieve the network interface status
        """
        return self._gateway.get('/status/network/ports/0')

    def ifconfig(self):
        """
        Retrieve the ip configuration
        """
        return self.ipconfig()

    def ipconfig(self):
        """
        Retrieve the ip configuration
        """
        return self._gateway.get('/config/network/ports/0')

    def set_static_ipaddr(self, address, subnet, gateway, primary_dns_server, secondary_dns_server=None):
        """
        Set a Static IP Address

        :param str address: The static address
        :param str subnet: The subnet for the static address
        :param str gateway: The default gateway
        :param str primary_dns_server: The primary DNS server
        :param str,optinal secondary_dns_server: The secondary DNS server, defaults to None
        """
        ip = self._gateway.get('/config/network/ports/0/ip')
        ip.DHCPMode = Mode.Disabled
        ip.address = address
        ip.netmask = subnet
        ip.gateway = gateway
        ip.autoObtainDNS = False
        ip.DNSServer1 = primary_dns_server

        if secondary_dns_server is not None:
            ip.DNSServer2 = secondary_dns_server

        logging.getLogger().info('Configuring a static ip address.')

        self._gateway.put('/config/network/ports/0/ip', ip)

        logging.getLogger().info(
            'Network settings updated. %s',
            {'address': address, 'subnet': subnet, 'gateway': gateway, 'DNS1': primary_dns_server, 'DNS2': secondary_dns_server}
        )

    def set_static_nameserver(self, primary_dns_server, secondary_dns_server=None):
        """
        Set the DNS Server addresses statically

        :param str primary_dns_server, The primary DNS server
        :param str,optinal secondary_dns_server, The secondary DNS server, defaults to None
        """
        ip = self._gateway.get('/config/network/ports/0/ip')
        ip.autoObtainDNS = False
        ip.DNSServer1 = primary_dns_server

        if secondary_dns_server is not None:
            ip.DNSServer2 = secondary_dns_server

        logging.getLogger().info('Configuring nameserver settings.')

        self._gateway.put('/config/network/ports/0/ip', ip)

        logging.getLogger().info('Nameserver settings updated. %s', {'DNS1': primary_dns_server, 'DNS2': secondary_dns_server})

    def enable_dhcp(self):
        """
        Enable DHCP
        """
        ip = self._gateway.get('/config/network/ports/0/ip')
        ip.DHCPMode = Mode.Enabled
        ip.autoObtainDNS = True

        logging.getLogger().info('Enabling DHCP.')

        self._gateway.put('/config/network/ports/0/ip', ip)

        logging.getLogger().info('Network settings updated. Enabled DHCP.')

    def tcp_connect(self, address, port):
        """
        Test a TCP connection between the gateway and the provided address

        :param str address: The address to test the connection to
        :param int port: The port of the address to test the connection to
        """
        param = Object()
        param.address = address
        param.port = port

        logging.getLogger().info("Testing connection. %s", {'address': address, 'port': port})

        task = self._gateway.execute("/status/network", "tcpconnect", param)
        try:
            task = TaskManager.wait(self._gateway, task)
            logging.getLogger().debug("Obtained connection status. %s", {'status': task.result.rc})
            if task.result.rc == "Open":
                return True
        except TaskManager.TaskError:
            pass

        logging.getLogger().warning("Couldn't establish TCP connection. %s", {'address': address, 'port': port})

        return False
