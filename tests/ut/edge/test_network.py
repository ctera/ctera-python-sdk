from unittest import mock
import munch

from cterasdk.edge import network
from cterasdk.edge.types import TCPService, TCPConnectResult, StaticRoute
from cterasdk.edge.enum import Mode, IPProtocol, Traffic
from cterasdk.common import Object
from cterasdk.exceptions.common import TaskException
from tests.ut.edge import base_edge


class TestEdgeNetwork(base_edge.BaseEdgeTest):  # pylint: disable=too-many-public-methods,too-many-instance-attributes

    def setUp(self):
        super().setUp()
        self._static_ip = Object()
        self._static_ip.DHCPMode = Mode.Disabled
        self._static_ip.address = '192.168.0.150'
        self._static_ip.netmask = '255.255.240.0'
        self._static_ip.gateway = '192.168.0.1'
        self._static_ip.autoObtainDNS = False
        self._static_ip.DNSServer1 = '192.168.0.2'
        self._static_ip.DNSServer2 = '192.168.0.3'

        self._dhcp_ip = Object()
        self._dhcp_ip.DHCPMode = Mode.Enabled
        self._dhcp_ip.address = '10.0.0.1'
        self._dhcp_ip.netmask = '255.255.255.0'
        self._dhcp_ip.gateway = '10.0.0.138'
        self._dhcp_ip.autoObtainDNS = True
        self._dhcp_ip.DNSServer1 = '10.0.0.2'
        self._dhcp_ip.DNSServer2 = '8.8.8.8'

        self._task_id = '138'
        self._tcp_connect_address = 'address'
        self._tcp_connect_port = 995

        self._mtu = 1320

        self._static_route_gateway = '192.168.0.150'
        self._static_route_netmask = '255.255.255.255'
        self._static_route_destination = '172.64.28.15'
        self._static_route_network = f'{self._static_route_destination}/32'

        self._proxy_address = '192.168.27.131'
        self._proxy_port = 3192
        self._proxy_user = 'admin'
        self._proxy_pass = 'password'

        self._hosts_ipaddr = '192.168.0.1'
        self._hosts_hostname = 'address.ctera.com'

    def test_network_status(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = network.LegacyNetwork(self._filer).get_status()
        self._filer.api.get('/status/network/ports/0')
        self.assertEqual(ret, get_response)

    def test_ifconfig(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = network.LegacyNetwork(self._filer).ifconfig()
        self._filer.api.get('/config/network/ports/0')
        self.assertEqual(ret, get_response)

    def test_ipconfig(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = network.LegacyNetwork(self._filer).ipconfig()
        self._filer.api.get('/config/network/ports/0')
        self.assertEqual(ret, get_response)

    def test_set_static_ip_addr(self):
        get_response = self._dhcp_ip
        self._init_filer(get_response=get_response)
        network.LegacyNetwork(self._filer).set_static_ipaddr(
            self._static_ip.address,
            self._static_ip.netmask,
            self._static_ip.gateway,
            self._static_ip.DNSServer1,
            self._static_ip.DNSServer2
        )
        self._filer.api.get.assert_called_once_with('/config/network/ports/0/ip')
        self._filer.api.put.assert_called_once_with('/config/network/ports/0/ip', mock.ANY)

        expected_param = self._static_ip
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_enable_dhcp(self):
        get_response = self._static_ip
        self._init_filer(get_response=get_response)
        network.LegacyNetwork(self._filer).enable_dhcp()
        self._filer.api.get.assert_called_once_with('/config/network/ports/0/ip')
        self._filer.api.put.assert_called_once_with('/config/network/ports/0/ip', mock.ANY)

        self._static_ip.DHCPMode = Mode.Enabled
        self._static_ip.autoObtainDNS = False
        expected_param = self._static_ip
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_set_static_primary_dns_server(self):
        self._dhcp_ip.secondary_dns_server = None
        get_response = self._dhcp_ip
        self._init_filer(get_response=get_response)
        network.LegacyNetwork(self._filer).set_static_nameserver(self._static_ip.DNSServer1)
        self._filer.api.get.assert_called_once_with('/config/network/ports/0/ip')
        self._filer.api.put.assert_called_once_with('/config/network/ports/0/ip', mock.ANY)

        self._dhcp_ip.DNSServer1 = self._static_ip.DNSServer1
        expected_param = self._dhcp_ip
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_set_static_primary_and_secondary_dns_servers(self):
        get_response = self._dhcp_ip
        self._init_filer(get_response=get_response)
        network.LegacyNetwork(self._filer).set_static_nameserver(self._static_ip.DNSServer1, self._static_ip.DNSServer2)
        self._filer.api.get.assert_called_once_with('/config/network/ports/0/ip')
        self._filer.api.put.assert_called_once_with('/config/network/ports/0/ip', mock.ANY)

        self._dhcp_ip.DNSServer1 = self._static_ip.DNSServer1
        self._dhcp_ip.DNSServer2 = self._static_ip.DNSServer2
        expected_param = self._dhcp_ip
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_tcp_connect_success(self):
        execute_response = self._task_id
        self._init_filer(execute_response=execute_response)

        task = Object()
        task.result = Object()
        task.result.rc = 'Open'
        self._filer.tasks.wait = mock.MagicMock(return_value=task)

        ret = network.LegacyNetwork(self._filer).diag.tcp_connect(TCPService(self._tcp_connect_address, self._tcp_connect_port))

        self._filer.api.execute.assert_called_once_with('/status/network', 'tcpconnect', mock.ANY)
        self._filer.tasks.wait.assert_called_once_with(self._task_id)

        expected_param = self._get_tcp_connect_object()
        actual_param = self._filer.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

        self.assertEqual(ret, TCPConnectResult(self._tcp_connect_address, self._tcp_connect_port, True))

    def test_tcp_connect_failure(self):
        execute_response = self._task_id
        self._init_filer(execute_response=execute_response)

        task = Object()
        task.result = Object()
        task.result.rc = 'BadAddress'
        self._filer.tasks.wait = mock.MagicMock(return_value=task)

        ret = network.LegacyNetwork(self._filer).diag.tcp_connect(TCPService(self._tcp_connect_address, self._tcp_connect_port))

        self._filer.api.execute.assert_called_once_with('/status/network', 'tcpconnect', mock.ANY)
        self._filer.tasks.wait.assert_called_once_with(self._task_id)

        expected_param = self._get_tcp_connect_object()
        actual_param = self._filer.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

        self.assertEqual(ret, TCPConnectResult(self._tcp_connect_address, self._tcp_connect_port, False))

    def test_iperf_success(self):
        execute_response = self._task_id
        self._init_filer(execute_response=execute_response)

        task = Object()
        task.result = Object()
        task.result.res = 'Success'

        self._filer.tasks.wait = mock.MagicMock(return_value=task)
        ret = network.LegacyNetwork(self._filer).diag.iperf(self._static_ip.address)

        expected_param = self._get_iperf_param()
        actual_param = self._filer.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

        self.assertEqual(ret, task.result.res)

    def _get_iperf_param(self, port=5201, threads=1, protocol=IPProtocol.TCP, direction=Traffic.Upload):
        param = Object()
        param._classname = 'IperfParam'  # pylint: disable=protected-access
        param.address = self._static_ip.address
        param.port = port
        param.threads = threads
        param.reverse = direction == Traffic.Download
        param.protocol = None if protocol == IPProtocol.TCP else IPProtocol.UDP
        return param

    def test_tcp_connect_task_error(self):
        execute_response = self._task_id
        self._init_filer(execute_response=execute_response)
        self._filer.tasks.wait = mock.MagicMock(side_effect=TaskException('Task failed', self._task_id))

        ret = network.LegacyNetwork(self._filer).diag.tcp_connect(TCPService(self._tcp_connect_address, self._tcp_connect_port))

        self._filer.api.execute.assert_called_once_with('/status/network', 'tcpconnect', mock.ANY)
        self._filer.tasks.wait.assert_called_once_with(self._task_id)

        expected_param = self._get_tcp_connect_object()
        actual_param = self._filer.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)

        self.assertEqual(ret, TCPConnectResult(self._tcp_connect_address, self._tcp_connect_port, False))

    def test_edge_set_mtu(self):
        get_response = TestEdgeNetwork._get_ethernet_object()
        self._init_filer(get_response=get_response)
        network.LegacyNetwork(self._filer).mtu.modify(self._mtu)
        self._filer.api.put.assert_called_once_with('/config/network/ports/0/ethernet', mock.ANY)
        expected_param = TestEdgeNetwork._get_ethernet_object(jumbo=True, mtu=self._mtu)
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def test_edge_reset_mtu(self):
        get_response = TestEdgeNetwork._get_ethernet_object(jumbo=True, mtu=1320)
        self._init_filer(get_response=get_response)
        network.LegacyNetwork(self._filer).mtu.reset()
        self._filer.api.put.assert_called_once_with('/config/network/ports/0/ethernet', mock.ANY)
        expected_param = TestEdgeNetwork._get_ethernet_object()
        actual_param = self._filer.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    @staticmethod
    def _get_ethernet_object(jumbo=False, mtu=1500):
        param = Object()
        param.jumbo = jumbo
        param.mtu = mtu
        return param

    def _get_tcp_connect_object(self):
        tcp_connect_param = Object()
        tcp_connect_param.address = self._tcp_connect_address
        tcp_connect_param.port = self._tcp_connect_port
        return tcp_connect_param

    def test_add_legacy_static_route(self):
        add_response = 'success'
        self._init_filer(add_response=add_response)
        ret = network.LegacyNetwork(self._filer).routes.add(self._static_route_gateway, self._static_route_network)
        self._filer.api.add.assert_called_once_with('/config/network/static_routes', mock.ANY)
        expected_param = Object(**{
            'GwIP': self._static_route_gateway,
            'DestIpMask': self._static_route_network.replace('/', '_')
        })
        actual_param = self._filer.api.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, add_response)

    def test_add_v711_static_route(self):
        add_response = 'success'
        self._init_filer(add_response=add_response, get_response=[
            Object(name='LAN0', ethernet=Object(mac='xyz')),
            Object(name='LAN1', ethernet=Object(mac='abc'))
        ])
        ret = network.Network711(self._filer).routes.add('LAN1', self._static_route_gateway, self._static_route_network)
        self._filer.api.add.assert_called_once_with('/config/network/ports/1/ipv4StaticRoutes', mock.ANY)
        expected_param = Object(**{
            'destination': self._static_route_destination,
            'netmask': self._static_route_netmask,
            'gateway': self._static_route_gateway
        })
        actual_param = self._filer.api.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, add_response)

    def test_get_all_static_routes(self):
        get_response = Object()
        get_response.ports = [Object(name='LAN')]
        get_response.static_routes = [Object(**{
            '_uuid': 'abc',
            'GwIP': self._static_route_gateway,
            'DestIpMask': self._static_route_network
        })]
        self._init_filer(get_response=get_response)
        ret = network.LegacyNetwork(self._filer).routes.get()
        self._filer.api.get.assert_called_once_with('/config/network')
        self.assertEqual(ret[0].gateway, get_response.static_routes[0].GwIP)
        self.assertEqual(ret[0].network, get_response.static_routes[0].DestIpMask)

    def test_remove_static_route(self):
        self._init_filer()
        route_uuid = '123'
        route = StaticRoute(route_uuid, 0, 'LAN', self._static_route_destination, self._static_route_gateway)
        network.LegacyNetwork(self._filer).routes.delete(route)
        self._filer.api.delete.assert_called_once_with(f'/config/network/static_routes/{route_uuid}')

    def test_clean_all_static_routes_success(self):
        execute_response = 'Success'
        self._init_filer(execute_response=execute_response)
        network.LegacyNetwork(self._filer).routes.clear()
        self._filer.api.execute.assert_called_once_with('/config/network', 'cleanStaticRoutes')

    def test_get_proxy_config(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = network.LegacyNetwork(self._filer).proxy.get_configuration()
        self._filer.api.get.assert_called_once_with('/config/network/proxy')
        self.assertEqual(ret, get_response)

    def test_is_proxy_enabled(self):
        for expected_response, configuration in [(False, 'NoProxy'), (True, 'Manual')]:
            self._init_filer(get_response=configuration)
            ret = network.LegacyNetwork(self._filer).proxy.is_enabled()
            self._filer.api.get.assert_called_once_with('/config/network/proxy/configurationMode')
            self.assertEqual(ret, expected_response)

    def test_disable_proxy(self):
        put_response = 'Success'
        self._init_filer(put_response=put_response)
        ret = network.LegacyNetwork(self._filer).proxy.disable()
        actual_param = self._filer.api.put.call_args[0][1]
        expected_param = TestEdgeNetwork._create_proxy_param(False)
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, put_response)

    def test_modify_proxy(self):
        put_response = 'Success'
        self._init_filer(put_response=put_response)
        ret = network.LegacyNetwork(self._filer).proxy.modify(self._proxy_address, self._proxy_port, self._proxy_user, self._proxy_pass)
        actual_param = self._filer.api.put.call_args[0][1]
        expected_param = TestEdgeNetwork._create_proxy_param(True, self._proxy_address, self._proxy_port,
                                                             self._proxy_user, self._proxy_pass)
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, put_response)

    @staticmethod
    def _create_proxy_param(enabled=None, address=None, port=None, username=None, password=None):
        m = munch.Munch({'_classname': 'ProxySettings'})
        m.configurationMode = 'Manual' if enabled else 'NoProxy'
        if enabled:
            m.port = port if port else 8080
        if address:
            m.address = address
        if username:
            m.username = username
        if password:
            m.password = password
        return m

    def test_get_hosts_file(self):
        get_response = 'Success'
        self._init_filer(get_response=get_response)
        ret = network.LegacyNetwork(self._filer).hosts.get()
        self._filer.api.get.assert_called_once_with('/config/network/hostsFileEntries')
        self.assertEqual(ret, get_response)

    def test_add_hosts_file_entry(self):
        add_response = 'Success'
        self._init_filer(add_response=add_response)
        ret = network.LegacyNetwork(self._filer).hosts.add(self._hosts_ipaddr, self._hosts_hostname)
        self._filer.api.add.assert_called_once_with('/config/network/hostsFileEntries', mock.ANY)
        actual_param = self._filer.api.add.call_args[0][1]
        expected_param = munch.Munch(dict(ip=self._hosts_ipaddr, hostName=self._hosts_hostname))
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, add_response)

    def test_delete_hosts_file_entry(self):
        delete_response = 'Success'
        self._init_filer(delete_response=delete_response)
        ret = network.LegacyNetwork(self._filer).hosts.delete(self._hosts_hostname)
        self._filer.api.delete.assert_called_once_with(f'/config/network/hostsFileEntries/{self._hosts_hostname}')
        self.assertEqual(ret, delete_response)
