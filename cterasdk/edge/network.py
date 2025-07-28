import logging

from ..exceptions import CTERAException
from ..exceptions.common import TaskException
from .enum import Mode, IPProtocol, Traffic
from .types import TCPConnectResult
from ..common import Object, parse_to_ipaddress
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


class Network(BaseCommand):
    """ Edge Filer Network configuration APIs """

    def __init__(self, portal):
        super().__init__(portal)
        self.proxy = Proxy(self._edge)
        self.mtu = MTU(self._edge)
        self.routes = StaticRoutes(self._edge)
        self.hosts = Hosts(self._edge)

    def get_status(self):
        """
        Retrieve the network interface status
        """
        return self._edge.api.get('/status/network/ports/0')

    def ifconfig(self):
        """
        Retrieve the ip configuration
        """
        return self.ipconfig()

    def ipconfig(self):
        """
        Retrieve the ip configuration
        """
        return self._edge.api.get('/config/network/ports/0')

    def set_static_ipaddr(self, address, subnet, gateway, primary_dns_server, secondary_dns_server=None):
        """
        Set a Static IP Address

        :param str address: The static address
        :param str subnet: The subnet for the static address
        :param str gateway: The default gateway
        :param str primary_dns_server: The primary DNS server
        :param str,optinal secondary_dns_server: The secondary DNS server, defaults to None
        """
        ip = self._edge.api.get('/config/network/ports/0/ip')
        ip.DHCPMode = Mode.Disabled
        ip.address = address
        ip.netmask = subnet
        ip.gateway = gateway
        ip.autoObtainDNS = False
        ip.DNSServer1 = primary_dns_server

        if secondary_dns_server is not None:
            ip.DNSServer2 = secondary_dns_server

        logger.info('Configuring a static ip address.')

        self._edge.api.put('/config/network/ports/0/ip', ip)

        logger.info(
            'Network settings updated. %s',
            {'address': address, 'subnet': subnet, 'gateway': gateway, 'DNS1': primary_dns_server, 'DNS2': secondary_dns_server}
        )

    def set_static_nameserver(self, primary_dns_server, secondary_dns_server=None):
        """
        Set the DNS Server addresses statically

        :param str primary_dns_server: The primary DNS server
        :param str,optinal secondary_dns_server: The secondary DNS server, defaults to None
        """
        ip = self._edge.api.get('/config/network/ports/0/ip')
        ip.autoObtainDNS = False
        ip.DNSServer1 = primary_dns_server

        if secondary_dns_server is not None:
            ip.DNSServer2 = secondary_dns_server

        logger.info('Configuring nameserver settings.')

        self._edge.api.put('/config/network/ports/0/ip', ip)

        logger.info('Nameserver settings updated. %s', {'DNS1': primary_dns_server, 'DNS2': secondary_dns_server})

    def enable_dhcp(self):
        """
        Enable DHCP
        """
        ip = self._edge.api.get('/config/network/ports/0/ip')
        ip.DHCPMode = Mode.Enabled
        ip.autoObtainDNS = True

        logger.info('Enabling DHCP.')

        self._edge.api.put('/config/network/ports/0/ip', ip)

        logger.info('Network settings updated. Enabled DHCP.')

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
        Test a TCP connection between the Edge Filer and the provided host address

        :param cterasdk.edge.types.TCPService service: A service, identified by a host and a port
        :returns: A named-tuple including the host, port and a boolean value indicating whether TCP connection can be established
        :rtype: cterasdk.edge.types.TCPConnectResult
        """
        param = Object()
        param.address = service.host
        param.port = service.port

        logger.info("Testing connection. %s", {'host': service.host, 'port': service.port})

        ref = self._edge.api.execute("/status/network", "tcpconnect", param)
        try:
            task = self._edge.tasks.wait(ref)
            logger.debug("Connection status: %s", task.result.rc)
            if task.result.rc == "Open":
                return TCPConnectResult(service.host, service.port, True)
        except TaskException:
            pass

        logger.warning("Couldn't establish TCP connection. %s", {'address': service.host, 'port': service.port})

        return TCPConnectResult(service.host, service.port, False)

    def iperf(self, address, port=5201, threads=1, protocol=IPProtocol.TCP, direction=Traffic.Upload, timeout=None):
        """
        Invoke a network throughput test

        :param str address: The host running the iperf server
        :param int,optional port: The iperf server port, defaults to 5201
        :param int,optional threads: The number of threads, defaults to 1
        :param cterasdk.edge.enum.IPProtocol,optional protocol: IP protocol, defaults to `'TCP'`
        :param cterasdk.edge.enum.Traffic,optional direction: Traffic direction, defaults to `'Upload'`
        :param float,optional timeout: Timeout (in seconds).
        :returns: A string containing the iperf output
        :rtype: str
        """
        param = Object()
        param._classname = 'IperfParam'  # pylint: disable=protected-access
        param.address = address
        param.port = port
        param.threads = threads
        param.reverse = direction == Traffic.Download
        param.protocol = None if protocol == IPProtocol.TCP else IPProtocol.UDP
        ref = self._edge.api.execute("/status/network", "iperf", param)
        try:
            task = self._edge.tasks.wait(ref, timeout)
            return task.result.res
        except TaskException as error:
            return error.task.result.res


class Proxy(BaseCommand):
    """Edge Filer Proxy Configuration APIs"""

    def get_configuration(self):
        """
        Get Proxy Configuration
        """
        return self._edge.api.get('/config/network/proxy')

    def is_enabled(self):
        """
        Check if Proxy Configuration is Enabled

        :returns: ``True`` if a proxy server was configured and ``False`` otherwise.
        :rtype: bool
        """
        return self._edge.api.get('/config/network/proxy/configurationMode') != 'NoProxy'

    def modify(self, address, port=None, username=None, password=None):
        """
        Modify Proxy Configuration

        :param str address: Proxy address
        :param int,optional port: Proxy port, defaults to ``8080``
        :param str,optional username: Username
        :param str,optional password: Password
        :returns: Proxy settings
        :rtype: cterasdk.common.object.Object
        """
        return self._configure(True, address, port, username, password)

    def _configure(self, enabled, address=None, port=None, username=None, password=None):
        param = Object()
        param._classname = 'ProxySettings'  # pylint: disable=protected-access
        param.configurationMode = 'Manual' if enabled else 'NoProxy'
        if enabled:
            param.port = port if port else 8080
            if address:
                param.address = address
            if username:
                param.username = username
            if password:
                param.password = password
        logger.info('Updating Proxy Server Configuration.')
        response = self._edge.api.put('/config/network/proxy', param)
        logger.info('Updated Proxy Server Configuration.')
        return response

    def disable(self):
        """
        Disable Proxy

        :returns: Proxy settings
        :rtype: cterasdk.common.object.Object
        """
        logger.info('Disabling Proxy.')
        return self._configure(False)


class MTU(BaseCommand):
    """Edge Filer MTU Configuration APIs"""

    def reset(self):
        """
        Set the default maximum transmission unit (MTU) settings
        """
        return self._configure(False, 1500)

    def modify(self, mtu):
        """
        Set a custom network maximum transmission unit (MTU)

        :param int mtu: Maximum transmission unit
        """
        return self._configure(True, mtu)

    def _configure(self, jumbo, mtu):
        settings = self._edge.api.get('/config/network/ports/0/ethernet')
        settings.jumbo = jumbo
        settings.mtu = mtu
        logger.info('Configuring MTU. %s', {'MTU': mtu})
        return self._edge.api.put('/config/network/ports/0/ethernet', settings)


class StaticRoutes(BaseCommand):
    """Edge Filer Static Route Configuration APIs"""

    def get(self):
        """
        Get All Static Routes
        """
        return self._edge.api.get('/config/network/static_routes')

    def add(self, source_ip, destination_ip_mask):
        """
        Add a Static Route

        :param str source_ip: The source IP (192.168.15.55)
        :param str destination_ip_mask: The destination IP and CIDR block (10.5.0.1/32)
        """
        try:
            param = Object()
            param.GwIP = str(parse_to_ipaddress(source_ip))
            param.DestIpMask = str(parse_to_ipaddress(destination_ip_mask)).replace("/", "_")
            res = self._edge.api.add('/config/network/static_routes', param)
            logger.info(
                "Static route updated. %s", {'Source': param.GwIP, 'Destination': destination_ip_mask})
            return res
        except CTERAException as error:
            logger.error("Static route creation failed.")
            raise CTERAException('Static route creation failed') from error

    def remove(self, destination_ip_mask):
        """
        Remove a Static Route

        :param str destination_ip_mask: The destination IP and CIDR block (10.5.0.1/32)
        """
        try:
            dest_ip_mask = str(parse_to_ipaddress(destination_ip_mask)).replace("/", "_")
            response = self._edge.api.delete(f'/config/network/static_routes/{dest_ip_mask}')
            logger.info(
                "Static route deleted. %s", {'Destination': dest_ip_mask})
            return response
        except CTERAException as error:
            logger.error("Static route deletion failed.")
            raise CTERAException('Static route deletion failed') from error

    def clear(self):
        """
        Clear All Static routes
        """
        try:
            self._edge.api.execute('/config/network', 'cleanStaticRoutes')
            logger.info('Static routes were deleted successfully')
        except CTERAException as error:
            logger.error("Failed to clear static routes")
            raise CTERAException('Failed to clear static routes') from error


class Hosts(BaseCommand):
    """Edge Filer Static Route Configuration APIs"""

    def get(self):
        """
        Get the Edge Filer's hosts file entries.
        """
        return self._edge.api.get('/config/network/hostsFileEntries')

    def add(self, ipaddr, hostname):
        """
        Add entry to the Edge Filer's hosts file.

        :param str ipaddr: IP Address
        :param str hostname: Hostname
        """
        param = Object(ip=ipaddr, hostName=hostname)
        return self._edge.api.add('/config/network/hostsFileEntries', param)

    def delete(self, hostname):
        return self._edge.api.delete(f'/config/network/hostsFileEntries/{hostname}')
