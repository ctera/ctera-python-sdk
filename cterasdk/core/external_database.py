from cterasdk.common import Object
from cterasdk.core.enum import DatabaseMode, ExternalDbAuthMethod
from cterasdk.exceptions import CTERAException
from cterasdk.lib.crypto import PrivateKey, X509Certificate

DEFAULT_EXT_DB_PORT = 5432
DEFAULT_EXT_DB_NAME = 'postgres'
DEFAULT_EXT_DB_SSL_MODE = 'verify-full'

_SSL_MODES_REQUIRING_CA = frozenset({'verify-ca', 'verify-full'})


def auth_method_to_schema_auth_mode(auth_method):
    if auth_method in (ExternalDbAuthMethod.Certificate, 'certificate', 'cert', 'Cert'):
        return 'Cert'
    if auth_method in (ExternalDbAuthMethod.Token, 'token', 'Token'):
        return 'Token'
    return 'Credentials'


def _normalize_database_mode(database_mode):
    if database_mode is None:
        return DatabaseMode.Embedded
    if database_mode in (DatabaseMode.Embedded, DatabaseMode.External):
        return database_mode
    if str(database_mode).lower() == DatabaseMode.External:
        return DatabaseMode.External
    if str(database_mode).lower() == DatabaseMode.Embedded:
        return DatabaseMode.Embedded
    raise CTERAException(f"Invalid database_mode: {database_mode}")


def _normalize_auth_method(ext_db_auth_method):
    if ext_db_auth_method is None:
        return ExternalDbAuthMethod.Credentials
    if ext_db_auth_method in (
            ExternalDbAuthMethod.Credentials,
            ExternalDbAuthMethod.Certificate,
            ExternalDbAuthMethod.Token,
    ):
        return ext_db_auth_method
    normalized = str(ext_db_auth_method).lower()
    if normalized in ('credentials', 'credential'):
        return ExternalDbAuthMethod.Credentials
    if normalized in ('certificate', 'cert'):
        return ExternalDbAuthMethod.Certificate
    if normalized == 'token':
        return ExternalDbAuthMethod.Token
    raise CTERAException(f"Invalid ext_db_auth_method: {ext_db_auth_method}")


def _normalize_ssl_mode(ssl_mode):
    if ssl_mode is None:
        return DEFAULT_EXT_DB_SSL_MODE
    mode = str(ssl_mode).lower()
    if mode == 'disable':
        raise CTERAException('ext_db_ssl_mode disable is not supported for external database mode')
    return ssl_mode


def _is_inline_pem(material):
    return isinstance(material, str) and '-----BEGIN' in material


def _pem_certificate_content(cert_material):
    if cert_material is None:
        return None
    if _is_inline_pem(cert_material):
        loaded = X509Certificate.from_string(cert_material)
    else:
        loaded = X509Certificate.load_certificate(cert_material)
    return loaded.pem_data.decode('utf-8')


def _pem_private_key_content(key_material):
    if key_material is None:
        return None
    if _is_inline_pem(key_material):
        loaded = PrivateKey.from_string(key_material)
    else:
        loaded = PrivateKey.load_private_key(key_material)
    return loaded.pem_data.decode('utf-8')


def _any_external_field_set(**fields):
    return any(value is not None for value in fields.values())


def resolve_init_database_configuration(  # pylint: disable=too-many-arguments,too-many-locals
        database_mode=DatabaseMode.Embedded,
        ext_db_host=None,
        ext_db_port=DEFAULT_EXT_DB_PORT,
        ext_db_name=DEFAULT_EXT_DB_NAME,
        ext_db_user=None,
        ext_db_password=None,
        ext_db_auth_method=None,
        ext_db_ssl_mode=None,
        ext_db_ssl_ca_cert=None,
        ext_db_ssl_client_cert=None,
        ext_db_ssl_client_key=None,
):
    mode = _normalize_database_mode(database_mode)
    auth_method = _normalize_auth_method(ext_db_auth_method)
    ssl_mode = _normalize_ssl_mode(ext_db_ssl_mode)

    ext_fields = {
        'ext_db_host': ext_db_host,
        'ext_db_port': ext_db_port if ext_db_port != DEFAULT_EXT_DB_PORT else None,
        'ext_db_name': ext_db_name if ext_db_name != DEFAULT_EXT_DB_NAME else None,
        'ext_db_user': ext_db_user,
        'ext_db_password': ext_db_password,
        'ext_db_auth_method': ext_db_auth_method,
        'ext_db_ssl_mode': ext_db_ssl_mode,
        'ext_db_ssl_ca_cert': ext_db_ssl_ca_cert,
        'ext_db_ssl_client_cert': ext_db_ssl_client_cert,
        'ext_db_ssl_client_key': ext_db_ssl_client_key,
    }

    if mode == DatabaseMode.Embedded:
        if _any_external_field_set(**ext_fields):
            raise CTERAException(
                'External database parameters require database_mode=external')
        return mode, None

    if auth_method == ExternalDbAuthMethod.Token:
        raise CTERAException('ext_db_auth_method token is not yet supported by the portal')

    if not ext_db_host:
        raise CTERAException('ext_db_host is required when database_mode is external')
    if not ext_db_user:
        raise CTERAException('ext_db_user is required when database_mode is external')

    if auth_method == ExternalDbAuthMethod.Credentials:
        if not ext_db_password:
            raise CTERAException(
                'ext_db_password is required when ext_db_auth_method is credentials')
    elif auth_method == ExternalDbAuthMethod.Certificate:
        if not ext_db_ssl_client_cert or not ext_db_ssl_client_key:
            raise CTERAException(
                'ext_db_ssl_client_cert and ext_db_ssl_client_key are required for certificate authentication')

    ssl_mode_normalized = str(ssl_mode).lower()
    if ssl_mode_normalized in _SSL_MODES_REQUIRING_CA and not ext_db_ssl_ca_cert:
        raise CTERAException(
            f'ext_db_ssl_ca_cert is required when ext_db_ssl_mode is {ssl_mode}')

    config = build_external_database_config(
        host=ext_db_host,
        port=ext_db_port,
        database_name=ext_db_name,
        username=ext_db_user,
        password=ext_db_password,
        ssl_mode=ssl_mode,
        auth_method=auth_method,
        ssl_ca_cert=ext_db_ssl_ca_cert,
        ssl_client_cert=ext_db_ssl_client_cert,
        ssl_client_key=ext_db_ssl_client_key,
    )
    return mode, config


def build_external_database_config(
        host,
        port=DEFAULT_EXT_DB_PORT,
        database_name=DEFAULT_EXT_DB_NAME,
        username=None,
        password=None,
        ssl_mode=DEFAULT_EXT_DB_SSL_MODE,
        auth_method=ExternalDbAuthMethod.Credentials,
        ssl_ca_cert=None,
        ssl_client_cert=None,
        ssl_client_key=None,
):
    config = Object()
    config._classname = 'ExternalDatabaseConfig'  # pylint: disable=protected-access
    config.host = host
    config.port = port
    config.databaseName = database_name
    config.username = username
    config.sslMode = ssl_mode
    config.authMode = auth_method_to_schema_auth_mode(auth_method)

    if password is not None:
        config.password = password

    ca_pem = _pem_certificate_content(ssl_ca_cert)
    if ca_pem is not None:
        config.sslCaCert = ca_pem

    client_cert_pem = _pem_certificate_content(ssl_client_cert)
    if client_cert_pem is not None:
        config.authCert = client_cert_pem

    client_key_pem = _pem_private_key_content(ssl_client_key)
    if client_key_pem is not None:
        config.authKey = client_key_pem

    return config


def apply_database_mode_to_init_params(params, database_mode, external_database_config):
    if database_mode != DatabaseMode.External:
        return
    params.databaseMode = DatabaseMode.External
    params.externalDatabaseConfig = external_database_config
