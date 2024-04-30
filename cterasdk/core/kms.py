import logging

from .base_command import BaseCommand
from ..common import Object, utf8_decode
from ..lib import X509Certificate, PrivateKey
from . import query


class KMS(BaseCommand):
    """
    External Key Management APIs
    :ivar cterasdk.core.kms.KMS servers: Object holding the Portal External Key Management Server APIs
    """

    def __init__(self, portal):
        super().__init__(portal)
        self.servers = KMSServers(self._core)

    def settings(self):
        """
        Get Key Management Service Settings
        """
        return self._core.api.get('/settings/keyManagerSettings')

    def status(self):
        """
        Get Key Management Service Status
        """
        return self._core.api.execute('', 'getKeyManagerGlobalStatus')

    def enable(self, private_key, client_certificate, server_certificate, expiration=None, timeout=None, port=None):
        """
        Enable Key Management Service

        :param str private_key: The PEM-encoded private key, or a path to the PEM-encoded private key file
        :param str client_certificate: The PEM-encoded client certificate, or a path to the certificate file
        :param str server_certificate: The PEM-encoded KMS server certificate, or a path to the certificate file
        :param int,optional expiration: Key expiration in days, defaults to ``365``.
        :param int,optional timeout: Connection timeout in seconds, defaults to ``2``
        :param int,optional port: Key server port, defaults to ``5696``
        """
        param = self._core.api.defaults('KeyManagerSettings')
        param.expiration = expiration if expiration else 365
        param.integration.connectionSettings.timeout = timeout if timeout else 2
        param.integration.connectionSettings.port = port if port else 5696
        param.integration.tlsDetails = self._TLS_details(private_key, client_certificate, server_certificate)
        logging.getLogger('cterasdk.core').info('Enabling Key Management Service')
        response = self._core.api.put('/settings/keyManagerSettings', param)
        logging.getLogger('cterasdk.core').info('Key Management Service enabled')
        return response

    @staticmethod
    def _TLS_details(private_key, client_certificate, server_certificate):
        param = Object()
        param._classname = 'TLSDetails'  # pylint: disable=protected-access
        param.files = Object()
        param.files._classname = 'TLSFiles'  # pylint: disable=protected-access
        param.files.clientCert = utf8_decode(X509Certificate.load_certificate(client_certificate).pem_data)
        param.files.privateKey = utf8_decode(PrivateKey.load_private_key(private_key).pem_data)
        param.files.rootCACert = utf8_decode(X509Certificate.load_certificate(server_certificate).pem_data)
        return param

    def disable(self):
        """
        Disable Key Management Service
        """
        logging.getLogger('cterasdk.core').info('Disabling Key Management Service')
        response = self._core.api.execute('', 'removeKeyManagementService')
        logging.getLogger('cterasdk.core').info('Key Management Service disabled')
        return response

    def modify(self, private_key=None, client_certificate=None, server_certificate=None, expiration=None, timeout=None, port=None):
        """
        Modify Key Management Service Settings

        :param str,optional private_key: The PEM-encoded private key, or a path to the PEM-encoded private key file
        :param str,optional client_certificate: The PEM-encoded client certificate, or a path to the certificate file
        :param str,optional server_certificate: The PEM-encoded KMS server certificate, or a path to the certificate file
        :param int,optional expiration: Key expiration in days, defaults to ``365``.
        :param int,optional timeout: Connection timeout in seconds, defaults to ``2``
        :param int,optional port: Key server port, defaults to ``5696``
        """

        settings = self.settings()
        if client_certificate:
            settings.integration.tlsDetails.files.clientCert = utf8_decode(X509Certificate.load_certificate(client_certificate).pem_data)
        if private_key:
            settings.integration.tlsDetails.files.privateKey = utf8_decode(PrivateKey.load_private_key(private_key).pem_data)
        if server_certificate:
            settings.integration.tlsDetails.files.rootCACert = utf8_decode(X509Certificate.load_certificate(server_certificate).pem_data)
        if expiration:
            settings.expiration = expiration
        if timeout:
            settings.integration.connectionSettings.timeout = timeout
        if port:
            settings.integration.connectionSettings.port = port

        logging.getLogger('cterasdk.core').info('Updating Key Management Service settings')
        response = self._core.api.put('/settings/keyManagerSettings', settings)
        logging.getLogger('cterasdk.core').info('Updated Key Management Service settings')
        return response


class KMSServers(BaseCommand):
    """ External Key Management Server APIs """

    def get(self, name):
        """
        Retrieve a key-server

        :param str name: Key-server name
        """
        return self._core.api.get(f'/keyManagerServers/{name}')

    def all(self):
        """
        List Key Management Servers
        """
        param = query.QueryParamBuilder().startFrom(0).countLimit(25).orFilter(True).build()
        return query.iterator(self._core, '/keyManagerServers', param)

    def add(self, name, ipaddr):
        """
        Add a key-server

        :param str name: Key-server name
        :param str ipaddr: Key-server IP address
        """
        param = Object()
        param._classname = 'KeyManagerServer'  # pylint: disable=protected-access
        param.name = name
        param.host = ipaddr
        logging.getLogger('cterasdk.core').info('Adding Key Server. %s', {'name': name, 'host': ipaddr})
        response = self._core.api.add('/keyManagerServers', param)
        logging.getLogger('cterasdk.core').info('Key Server. %s Added', {'name': name, 'host': ipaddr})
        return response

    def modify(self, current_name, new_name):
        """
        Remove a key-server

        :param str current_name: Key-server current name
        :param str new_name: Key-server new name
        """
        key_server = self.get(current_name)
        key_server.name = new_name
        logging.getLogger('cterasdk.core').info("Modifying Key Server. %s", {'name': current_name})
        response = self._core.api.put(f'/keyManagerServers/{current_name}', key_server)
        logging.getLogger('cterasdk.core').info("Key Server modified. %s", {'name': current_name})
        return response

    def delete(self, name):
        """
        Remove a key-server

        :param str name: Key-server name
        """
        logging.getLogger('cterasdk.core').info('Deleting Key Server. %s', {'name': name})
        response = self._core.api.delete(f'/keyManagerServers/{name}')
        logging.getLogger('cterasdk.core').info('Key Server deleted. %s', {'name': name})
        return response
