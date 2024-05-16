import logging

from .base_command import BaseCommand
from ..lib import X509Certificate, PrivateKey, create_certificate_chain
from ..common import Object


def initialize(edge):
    """
    Conditional intialization of the Edge Filer SSL Module.
    """
    if edge.session().version > '7.8':
        return SSLv78(edge)
    return SSLv1(edge)


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
        return self._edge.api.get('/config/fileservices/webdav/forceHttps')

    def _set_force_https(self, force):
        self._edge.api.put('/config/fileservices/webdav/forceHttps', force)

    def _import_certificate(self, path, private_key, *certificates):
        key_object = PrivateKey.load_private_key(private_key)
        certificates = [X509Certificate.load_certificate(certificate) for certificate in certificates]
        certificate_chain = [certificate.pem_data.decode('utf-8') for certificate in create_certificate_chain(*certificates)]
        server_certificate = ''.join([key_object.pem_data.decode('utf-8')] + certificate_chain)
        logging.getLogger('cterasdk.edge').info("Uploading Web Server SSL certificate.")
        response = self._edge.api.put(path, f"\n{server_certificate}")
        logging.getLogger('cterasdk.edge').info("Uploaded Web Server SSL certificate.")
        return response


class SSLv1(SSL):
    """ Edge Filer SSLv1 APIs """

    def remove_storage_ca(self):
        """
        Remove object storage trusted CA certificate
        """
        self._edge.api.put('/config/extStorageTrustedCA', None)

    def get_storage_ca(self):
        """
        Get object storage trusted CA certificate
        """
        return self._edge.api.get('/status/extStorageTrustedCA')

    def import_storage_ca(self, certificate):
        """
        Import the object storage trusted CA certificate

        :param str certificate: The PEM-encoded certificate or a path to the PEM-encoded server certificate file
        """
        logging.getLogger('cterasdk.edge').info('Setting trusted object storage CA certificate')
        param = Object()
        param._classname = 'ExtTrustedCA'  # pylint: disable=protected-access
        param.certificate = X509Certificate.load_certificate(certificate).pem_data.decode('utf-8')
        logging.getLogger('cterasdk.edge').info("Uploading object storage certificate.")
        response = self._edge.api.put('/config/extStorageTrustedCA', param)
        logging.getLogger('cterasdk.edge').info("Uploaded object storage certificate.")
        return response

    def import_certificate(self, private_key, *certificates):
        """
        Import the Edge Filer's web server's SSL certificate

        :param str private_key: The PEM-encoded private key, or a path to the PEM-encoded private key file
        :param list[str] certificates: The PEM-encoded certificates, or a list of paths to the PEM-encoded certificates
        """
        return self._import_certificate('/config/certificate', private_key, *certificates)


class SSLv78(SSL):
    """ Edge Filer v7.8 SSL Certificate APIs """

    def __init__(self, edge):
        super().__init__(edge)
        self.server = ServerCertificate(edge)
        self.ca = TrustedCAs(edge)


class ServerCertificate(BaseCommand):
    """ Edge Filer v7.8 Server Certificate APIs """

    def get(self):
        """
        Get Server Cerificate.
        """
        return self._edge.api.get('/proc/certificates/serverCertificate')

    def regenerate(self):
        """
        Generate a Self Signed Certificate.
        """
        logging.getLogger('cterasdk.edge').info("Generating a Self Signed Certificate.")
        response = self._edge.api.execute('/config/certificates', 'createSelfSign')
        logging.getLogger('cterasdk.edge').info("Generated a Self Signed Certificate.")
        return response

    def import_certificate(self, private_key, *certificates):
        """
        Import the Edge Filer's server SSL certificate

        :param str private_key: The PEM-encoded private key, or a path to the PEM-encoded private key file
        :param list[str] certificates: The PEM-encoded certificates, or a list of paths to the PEM-encoded certificates
        """
        return self._import_certificate('/config/certificates/serverCertificate', private_key, *certificates)


class TrustedCAs(BaseCommand):
    """ Edge Filer v7.8 Trusted CAs APIs """

    def all(self):
        """
        List Trusted CAs.
        """
        return self._edge.api.get('/proc/certificates/trustedCACertificates')

    def add(self, ca):
        """
        Add Trusted CA.

        :param str certificate: The PEM-encoded certificate or a path to the PEM-encoded server certificate file
        """
        certificate = X509Certificate.load_certificate(ca).pem_data.decode('utf-8')
        return self._edge.api.execute('/config/certificates', 'addTrustedCACert', certificate)

    def remove(self, ca):
        """
        Remove Trusted CA.

        :param object ca: CA fingerprint as `str`, or a trusted CA object.
        """
        fingerprint = None
        if isinstance(ca, Object) and hasattr(ca, 'fingerprint'):
            fingerprint = ca.fingerprint
        else:
            fingerprint = ca

        if fingerprint:
            logging.getLogger('cterasdk.edge').info("Removing Trusted CA. %s", {'fingerprint': fingerprint})
            response = self._edge.api.delete(f'/config/certificates/trustedCACertificates/{fingerprint}')
            logging.getLogger('cterasdk.edge').info("Removed Trusted CA. %s", {'fingerprint': fingerprint})
            return response

        raise ValueError('Could not identify CA fingerprint.')

    def clear(self):
        """
        Remove all Trusted CAs.
        """
        logging.getLogger('cterasdk.edge').info("Removing all Trusted CAs.")
        for ca in self.all():
            self.remove(ca)
