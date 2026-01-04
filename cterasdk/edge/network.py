import logging
from abc import abstractmethod
from contextlib import contextmanager
import ipaddress

from ..exceptions.common import TaskException
from .enum import Mode, IPProtocol, Traffic
from .types import TCPConnectResult, StaticRoute, NetworkInterface
from ..common import Object, BaseModule
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.edge')


class NetworkModule(BaseModule):

    def initialize_version(self, software_version):
        return Network711 if software_version > '7.9' else LegacyNetwork


class Network(BaseCommand):

    def __init__(self, edge):
        super().__init__(edge)
        self.hosts = Hosts(self._edge)
        self.proxy = Proxy(self._edge)
        self.diag = Diagnostics(self._edge)

    def interface(self, name):
        """
        Get Network Interface

        :param str name: Interface name
        """
        for interface in self.interfaces:
            if interface.name == name:
                return interface
        raise ValueError(f'Could not find interface: {name}.')

    def port(self, name):
        """
        Get Port

        :param str name: Interface name
        """
        return self.interface(name).port

    def deduce_port(self, interface):
        return interface if interface in [0, 1] else self.port(interface)

    @property
    def interfaces(self):
        """
        Get Network Interfaces.

        :returns: A list of network interfaces
        :rtype: list[cterasdk.edge.types.NetworkInterface]
        """
        return [NetworkInterface(i, interface.name, interface.ethernet.mac)
                for i, interface in enumerate(self._edge.api.get('/status/network/ports'))]

    def status(self, interface):
        """
        Get Interface Status.

        :param object interface: Interface name or port number
        """
        return self._edge.api.get(f'/status/network/ports/{self.deduce_port(interface)}')

    def ipconfig(self, interface):
        """
        Get Interface Configuration

        :param object interface: Interface name or port number
        """
        return self._edge.api.get(f'/config/network/ports/{self.deduce_port(interface)}')

    def set_static_ipaddr(self, interface, address, subnet, gateway, primary_dns_server, secondary_dns_server=None):
        """
        Set a Static IP Address

        :param object interface: Interface name or port number
        :param str address: The static address
        :param str subnet: The subnet for the static address
        :param str gateway: The default gateway
        :param str primary_dns_server: The primary DNS server
        :param str,optinal secondary_dns_server: The secondary DNS server, defaults to None
        """
        port = self.deduce_port(interface)
        ip = self._edge.api.get(f'/config/network/ports/{port}/ip')
        ip.DHCPMode = Mode.Disabled
        ip.address = address
        ip.netmask = subnet
        ip.gateway = gateway
        ip.autoObtainDNS = False
        ip.DNSServer1 = primary_dns_server

        if secondary_dns_server is not None:
            ip.DNSServer2 = secondary_dns_server

        logger.info('Updating network configuration: IP Configuration')
        self._edge.api.put(f'/config/network/ports/{port}/ip', ip)
        logger.info(
            'Network configuration updated. %s',
            {'address': address, 'subnet': subnet, 'gateway': gateway, 'DNS1': primary_dns_server, 'DNS2': secondary_dns_server}
        )

    def set_static_nameserver(self, interface, primary_dns_server, secondary_dns_server=None):
        """
        Set Static DNS Servers

        :param object interface: Interface name or port number
        :param str primary_dns_server: Primary DNS server
        :param str,optional secondary_dns_server: Secondary DNS server, defaults to None
        """
        port = self.deduce_port(interface)
        ip = self._edge.api.get(f'/config/network/ports/{port}/ip')
        ip.autoObtainDNS = False
        ip.DNSServer1 = primary_dns_server

        if secondary_dns_server is not None:
            ip.DNSServer2 = secondary_dns_server

        logger.info('Updating network configuration: DNS.')
        self._edge.api.put(f'/config/network/ports/{port}/ip', ip)
        logger.info('Network configuration updated. %s', {'DNS1': primary_dns_server, 'DNS2': secondary_dns_server})

    def enable_dhcp(self, interface):
        """
        Enable DHCP

        :param object interface: Interface name or port number
        """
        port = self.deduce_port(interface)
        ip = self._edge.api.get(f'/config/network/ports/{port}/ip')
        ip.DHCPMode = Mode.Enabled
        ip.autoObtainDNS = True
        logger.info('Updating network configuration: Enabling DHCP.')
        self._edge.api.put(f'/config/network/ports/{port}/ip', ip)
        logger.info('Network configuration updated. Enabled DHCP.')


class Network711(Network):
    """ Edge Filer v7.11 Network API """

    def __init__(self, edge):
        super().__init__(edge)
        self.mtu = MTU711(self._edge)
        self.routes = StaticRoutes711(self._edge)


class LegacyNetwork(Network):
    """ Edge Filer Legacy Network API """

    def __init__(self, edge):
        super().__init__(edge)
        self.mtu = LegacyMTU(self._edge)
        self.routes = LegacyStaticRoutes(self._edge)

    def get_status(self):
        """
        Retrieve the network interface status
        """
        return super().status(0)

    def ifconfig(self):
        """
        Retrieve the IP address settings
        """
        return super().ipconfig(0)

    def ipconfig(self):  # pylint: disable=arguments-differ
        """
        Retrieve the IP address settings
        """
        return super().ipconfig(0)

    def set_static_ipaddr(self, address, subnet, gateway,  # pylint: disable=arguments-differ
                          primary_dns_server, secondary_dns_server=None):
        return super().set_static_ipaddr(0, address, subnet, gateway, primary_dns_server, secondary_dns_server)

    def set_static_nameserver(self, primary_dns_server, secondary_dns_server=None):  # pylint: disable=arguments-differ
        return super().set_static_nameserver(0, primary_dns_server, secondary_dns_server)

    def enable_dhcp(self):  # pylint: disable=arguments-differ
        return super().enable_dhcp(0)


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


class BaseMTU(BaseCommand):

    def reset(self, interface):  # pylint: disable=arguments-differ
        return self._update_max_transmission_unit(interface, False, 1500)

    def modify(self, interface, size):  # pylint: disable=arguments-differ
        return self._update_max_transmission_unit(interface, True, size)

    def _update_max_transmission_unit(self, interface, jumbo, size):
        port = self._edge.network.deduce_port(interface)
        settings = self._edge.api.get(f'/config/network/ports/{port}/ethernet')
        settings.jumbo = jumbo
        settings.mtu = size
        logger.info('Configuring %s MTU for interface: %s', size, port)
        return self._edge.api.put(f'/config/network/ports/{port}/ethernet', settings)


class MTU711(BaseMTU):
    """Multi Network Interface MTU Configuration"""


class LegacyMTU(BaseMTU):
    """Single Network Interface MTU Configuration"""

    def reset(self):  # pylint: disable=arguments-differ
        """
        Reset to defaults.
        """
        super().reset(0)

    def modify(self, size):  # pylint: disable=arguments-differ
        """
        Set Custom Network Maximum Transmission Unit (MTU)

        :param int size: Maximum Transmission Unit
        """
        super().modify(0, size)


class BaseStaticRoutes(BaseCommand):
    """Edge Filer Static Routes Configuration"""

    @staticmethod
    @contextmanager
    def _validate_route(gateway, network):
        yield str(ipaddress.ip_address(gateway)), ipaddress.ip_network(network)

    def add(self, interface, route_gateway, route_network):  # pylint: disable=arguments-differ
        """
        Add a route.

        :param object interface: Interface name or port number
        :param str route_gateway: Gateway IP address
        :param str route_network: Network (CIDR)
        """
        with BaseStaticRoutes._validate_route(route_gateway, route_network) as (gateway, network):
            ip_network = str(network)
            logger.info('Adding route for network: %s, to: %s', ip_network, gateway)
            response = self._add_route(interface, gateway, network)
            logger.info('Route added for network: %s, to: %s', ip_network, gateway)
            return response

    @abstractmethod
    def _add_route(self, interface, gateway, network):
        raise NotImplementedError('Subclass must implement the "_add_route" method.')

    def delete(self, route):
        """
        Delete a route.

        :param cterasdk.edge.types.StaticRoute route: Static Route
        """
        logger.info('Deleting route. Network: %s, Gateway: %s', route.network, route.gateway)
        self._edge.api.delete(f'/config/network/static_routes/{route.id}')
        logger.info('Route deleted. Network: %s, Gateway: %s', route.network, route.gateway)

    def clear(self):
        logger.info('Clearing route table.')
        self._edge.api.execute('/config/network', 'cleanStaticRoutes')
        logger.info('Route table cleared.')


class StaticRoutes711(BaseStaticRoutes):
    """Edge Filer 7.11 Static Routes Configuration"""

    def get(self):
        """
        Get Routes.
        """
        routes = []
        for port, interface in enumerate(self._edge.api.get('/config/network/ports')):
            for route in interface.ipv4StaticRoutes:
                ip_network = str(ipaddress.IPv4Network(f'{route.destination}/{route.netmask}', False))
                routes.append(StaticRoute(interface._uuid, port,  # pylint: disable=protected-access
                                          interface.name, ip_network, route.gateway))
        return routes

    def _add_route(self, interface, gateway, network):
        port = self._edge.network.deduce_port(interface)
        param = Object()
        param.destination = str(network.network_address)
        param.netmask = str(network.netmask)
        param.gateway = gateway
        return self._edge.api.add(f'/config/network/ports/{port}/ipv4StaticRoutes', param)


class LegacyStaticRoutes(BaseStaticRoutes):
    """Legacy Static Routes Configuration"""

    def get(self):
        """
        Get Routes.
        """
        network = self._edge.api.get('/config/network')
        return [StaticRoute(
            r._uuid, 0, network.ports[0].name,  # pylint: disable=protected-access
            str(ipaddress.IPv4Network(r.DestIpMask.replace('_', '/'), False)), r.GwIP
        ) for r in network.static_routes]

    def add(self, gateway, network):  # pylint: disable=arguments-differ
        """
        Add a route.

        :param str gateway: Gateway IP address
        :param str network: Network (CIDR)
        """
        return super().add(0, gateway, network)

    def _add_route(self, interface, gateway, network):  # pylint: disable=unused-argument
        param = Object()
        param.GwIP = gateway
        param.DestIpMask = str(network).replace('/', '_')
        return self._edge.api.add('/config/network/static_routes', param)


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


class Diagnostics(BaseCommand):

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
