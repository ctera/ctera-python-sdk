import logging

from cterasdk.exception import CTERAException
from .enum import Mode, IPProtocol, Traffic
from .types import TCPConnectResult
from ..lib.task_manager_base import TaskError
from ..common import Object, parse_to_ipaddress
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

        :param str primary_dns_server: The primary DNS server
        :param str,optinal secondary_dns_server: The secondary DNS server, defaults to None
        """
        ip = self._gateway.get('/config/network/ports/0/ip')
        ip.autoObtainDNS = False
        ip.DNSServer1 = primary_dns_server

        if secondary_dns_server is not None:
            ip.DNSServer2 = secondary_dns_server

        logging.getLogger().info('Configuring nameserver settings.')

        self._gateway.put('/config/network/ports/0/ip', ip)

        logging.getLogger().info('Nameserver settings updated. %s', {'DNS1': primary_dns_server, 'DNS2': secondary_dns_server})

    def reset_mtu(self):
        """
        Set the default maximum transmission unit (MTU) settings
        """
        self._set_mtu(False, 1500)

    def set_mtu(self, mtu):
        """
        Set a custom network maximum transmission unit (MTU)

        :param int mtu: Maximum transmission unit
        """
        self._set_mtu(True, mtu)

    def _set_mtu(self, jumbo, mtu):
        settings = self._gateway.get('/config/network/ports/0/ethernet')
        settings.jumbo = jumbo
        settings.mtu = mtu
        return self._gateway.put('/config/network/ports/0/ethernet', settings)

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

    def diagnose(self, services):
        """
        Test a TCP connection to a host over a designated port

        :param list[cterasdk.edge.types.TCPService] services: List of services, identified by a host and a port
        :returns: A list of named-tuples including the host, port and a boolean value indicating whether TCP connection can be established
        :rtype: list[cterasdk.edge.types.TCPConnectResult]
        """
        return [self.tcp_connect(service) for service in services]

    def tcp_connect(self, service):
        """
        Test a TCP connection between the Gateway and the provided host address

        :param cterasdk.edge.types.TCPService service: A service, identified by a host and a port
        :returns: A named-tuple including the host, port and a boolean value indicating whether TCP connection can be established
        :rtype: cterasdk.edge.types.TCPConnectResult
        """
        param = Object()
        param.address = service.host
        param.port = service.port

        logging.getLogger().info("Testing connection. %s", {'host': service.host, 'port': service.port})

        task = self._gateway.execute("/status/network", "tcpconnect", param)
        try:
            task = self._gateway.tasks.wait(task)
            logging.getLogger().debug("Obtained connection status. %s", {'status': task.result.rc})
            if task.result.rc == "Open":
                return TCPConnectResult(service.host, service.port, True)
        except TaskError:
            pass

        logging.getLogger().warning("Couldn't establish TCP connection. %s", {'address': service.host, 'port': service.port})

        return TCPConnectResult(service.host, service.port, False)

    def iperf(self, address, port=5201, threads=1, protocol=IPProtocol.TCP, direction=Traffic.Upload, retries=120, seconds=1):
        """
        Invoke a network throughput test

        :param str address: The host running the iperf server
        :param int,optional port: The iperf server port, defaults to 5201
        :param int,optional threads: The number of threads, defaults to 1
        :param cterasdk.edge.enum.IPProtocol,optional protocol: IP protocol, defaults to `'TCP'`
        :param cterasdk.edge.enum.Traffic,optional direction: Traffic direction, defaults to `'Upload'`
        :param int,optional retries: Number of retries when sampling the iperf task status, defaults to 120
        :param int,optional seconds: Number of seconds to wait between retries, defaults to 1
        :returns: A string containing the iperf output
        :rtype: str
        """
        param = Object()
        param._classname = 'IperfParam'  # pylint: disable=protected-access
        param.address = address
        param.port = port
        param.threads = threads
        param.reverse = (direction == Traffic.Download)
        param.protocol = None if protocol == IPProtocol.TCP else IPProtocol.UDP
        task = self._gateway.execute("/status/network", "iperf", param)
        try:
            task = self._gateway.tasks.wait(task, retries, seconds)
            return task.result.res
        except TaskError as error:
            return error.task.result.res

    def get_static_routes(self):
        """
        Get all Static Routes
        """
        return self._gateway.get('/config/network/static_routes')

    def add_static_route(self, source_ip, destination_ip_mask):
        """
        Set a Static Route

        :param str source_ip: The source IP (192.168.15.55)
        :param str destination_ip_mask: The destination IP and CIDR block (10.5.0.1/32)
        """
        try:
            param = Object()
            param.GwIP = str(parse_to_ipaddress(source_ip))
            param.DestIpMask = str(parse_to_ipaddress(destination_ip_mask)).replace("/", "_")
            res = self._gateway.add('/config/network/static_routes', param)
            logging.getLogger().info(
                "Static route updated. %s", {'Source': param.GwIP, 'Destination': destination_ip_mask})
            return res
        except CTERAException as error:
            logging.getLogger().error("Static route creation failed.")
            raise CTERAException('Static route creation failed', error)

    def remove_static_route(self, destination_ip_mask):
        """
        Delete a Static Route

        :param str destination_ip_mask: The destination IP and CIDR block (10.5.0.1/32)
        """
        try:
            dest_ip_mask = str(parse_to_ipaddress(destination_ip_mask)).replace("/", "_")
            response = self._gateway.delete(f'/config/network/static_routes/{dest_ip_mask}')
            logging.getLogger().info(
                "Static route deleted. %s", {'Destination': dest_ip_mask})
            return response
        except CTERAException as error:
            logging.getLogger().error("Static route deletion failed.")
            raise CTERAException('Static route deletion failed', error)

    def clean_all_static_routes(self):
        """
        Clean all Static routes
        """
        try:
            self._gateway.execute('/config/network', 'cleanStaticRoutes')
            logging.getLogger().info('Static routes were deleted successfully')
        except CTERAException as error:
            logging.getLogger().error("Failed to clean Static routes")
            raise CTERAException('Failed to delete Static routes', error)
