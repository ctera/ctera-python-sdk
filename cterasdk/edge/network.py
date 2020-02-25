import logging

from .enum import Mode
from . import taskmgr as TaskManager
from ..common import Object
from .base_command import BaseCommand


class Network(BaseCommand):

    def set_static_ipaddr(self, address, subnet, gateway, DNSServer1, DNSServer2=None):
        ip = self._gateway.get('/config/network/ports/0/ip')
        ip.DHCPMode = Mode.Disabled
        ip.address = address
        ip.netmask = subnet
        ip.gateway = gateway
        ip.autoObtainDNS = False
        ip.DNSServer1 = DNSServer1

        if DNSServer2 is not None:
            ip.DNSServer2 = DNSServer2

        logging.getLogger().info('Configuring a static ip address.')

        self._gateway.put('/config/network/ports/0/ip', ip)

        logging.getLogger().info(
            'Network settings updated. %s',
            {'address': address, 'subnet': subnet, 'gateway': gateway, 'DNS1': DNSServer1, 'DNS2': DNSServer2}
        )

    def set_static_nameserver(self, DNSServer1, DNSServer2=None):
        ip = self._gateway.get('/config/network/ports/0/ip')
        ip.autoObtainDNS = False
        ip.DNSServer1 = DNSServer1

        if DNSServer2 is not None:
            ip.DNSServer2 = DNSServer2

        logging.getLogger().info('Configuring nameserver settings.')

        self._gateway.put('/config/network/ports/0/ip', ip)

        logging.getLogger().info('Nameserver settings updated. %s', {'DNS1': DNSServer1, 'DNS2': DNSServer2})

    def enable_dhcp(self):
        ip = self._gateway.get('/config/network/ports/0/ip')
        ip.DHCPMode = Mode.Enabled
        ip.autoObtainDNS = True

        logging.getLogger().info('Enabling DHCP.')

        self._gateway.put('/config/network/ports/0/ip', ip)

        logging.getLogger().info('Network settings updated. Enabled DHCP.')

    def tcp_connect(self, address, port):
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
