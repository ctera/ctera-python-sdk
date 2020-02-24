import os
import ssl

from ..lib import TempfileServices


class CertificateServices:

    @staticmethod
    def add_trusted_cert(host, port):
        fd, filepath = TempfileServices.mkfile(host, '.crt')
        pem = ssl.get_server_certificate((host, port))
        os.write(fd, pem.encode())
        os.close(fd)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        context.load_verify_locations(filepath)
        return context
