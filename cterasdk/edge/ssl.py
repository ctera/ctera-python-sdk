import logging

from .base_command import BaseCommand
from ..lib import X509Certificate, PrivateKey, create_certificate_chain
from ..common import Object


class SSL(BaseCommand):
    """ Edge Filer SSL APIs """

    def enable_http(self):
        """
        Enable HTTP access
        """
        self._set_force_https(False)

    def disable_http(self):
        """
        Disable HTTP access
        """
        self._set_force_https(True)

    def is_http_disabled(self):
        """
        Check if HTTP access is disabled
        """
        return self._get_force_https()

    def is_http_enabled(self):
        """
        Check if HTTP access is enabled
        """
        return not self._get_force_https()

    def _get_force_https(self):
        return self._gateway.get('/config/fileservices/webdav/forceHttps')

    def _set_force_https(self, force):
        self._gateway.put('/config/fileservices/webdav/forceHttps', force)

    def remove_storage_ca(self):
        """
        Remove object storage trusted CA certificate
        """
        self._gateway.put('/config/extStorageTrustedCA', None)

    def get_storage_ca(self):
        """
        Get object storage trusted CA certificate
        """
        return self._gateway.get('/status/extStorageTrustedCA')

    def import_storage_ca(self, certificate):
        """
        Import the object storage trusted CA certificate

        :param str certificate: The PEM-encoded certificate or a path to the PEM-encoded server certificate file
        """
        logging.getLogger().info('Setting trusted object storage CA certificate')
        param = Object()
        param._classname = 'ExtTrustedCA'  # pylint: disable=protected-access
        param.certificate = X509Certificate.load_certificate(certificate).pem_data.decode('utf-8')
        logging.getLogger().info("Uploading object storage certificate.")
        response = self._gateway.put('/config/extStorageTrustedCA', param)
        logging.getLogger().info("Uploaded object storage certificate.")
        return response

    def import_certificate(self, private_key, *certificates):
        """
        Import the Edge Filer's web server's SSL certificate

        :param str private_key: The PEM-encoded private key, or a path to the PEM-encoded private key file
        :param list[str] certificates: The PEM-encoded certificates, or a list of paths to the PEM-encoded certificates
        """

        key_object = PrivateKey.load_private_key(private_key)
        certificates = [X509Certificate.load_certificate(certificate) for certificate in certificates]
        certificate_chain = [certificate.pem_data.decode('utf-8') for certificate in create_certificate_chain(*certificates)]
        server_certificate = ''.join([key_object.pem_data.decode('utf-8')] + certificate_chain)
        logging.getLogger().info("Uploading SSL certificate.")
        response = self._gateway.put('/config/certificate', f"\n{server_certificate}")
        logging.getLogger().info("Uploaded SSL certificate.")
        return response
