import socket

from cterasdk import exception
from cterasdk.common import Object
from tests.ut import base_edge


class TestObjectEdge(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._host = ''
        self._port = 80
        self._socket_connect_mock = self.patch_call("cterasdk.client.host.socket.socket.connect_ex")

    def test_connection_success(self):
        get_response = Object()
        get_response.hostname = self._filer.host()
        self._init_filer(get_response=get_response)
        self._socket_connect_mock.return_value = 0

        self._filer.test()

        self._socket_connect_mock.assert_called_once_with((self._host, self._port))
        self._filer.get.assert_called_once_with('/nosession/logininfo')

    def test_connection_socket_connect_error(self):
        get_response = Object()
        get_response.hostname = self._filer.host()
        self._init_filer(get_response=get_response)
        self._socket_connect_mock.side_effect = socket.gaierror()

        with self.assertRaises(exceptions.HostUnreachable) as error:
            self._filer.test()

        self._socket_connect_mock.assert_called_once_with((self._host, self._port))
        self.assertEqual('Unable to reach host', error.exception.message)

    def test_connection_socket_connect_error_none_zero_rc(self):
        get_response = Object()
        get_response.hostname = self._filer.host()
        self._init_filer(get_response=get_response)
        self._socket_connect_mock.return_value = 1

        with self.assertRaises(exceptions.HostUnreachable) as error:
            self._filer.test()

        self._socket_connect_mock.assert_called_once_with((self._host, self._port))
        self.assertEqual('Unable to reach host', error.exception.message)
