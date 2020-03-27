import os
import ssl

from ..lib import TempfileServices


class CertificateServices:

    @staticmethod
    def add_trusted_cert(host, port):
        filepath = CertificateServices.save_cert_from_server(host, port)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.load_verify_locations(filepath)
        return context

    @staticmethod
    def save_cert_from_server(host, port):
        fd, filepath = TempfileServices.mkfile(host, '.pem')
        pem = ssl.get_server_certificate((host, port))
        os.write(fd, pem.encode())
        os.close(fd)
        return filepath
