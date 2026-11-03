import logging
import time

from .base_command import BaseCommand
from .enum import DatabaseMode, ServerMode, SetupWizardStage, SetupWizardStatus, SlaveAuthenticaionMethod
from .external_database import (
    DEFAULT_EXT_DB_NAME,
    DEFAULT_EXT_DB_PORT,
    DEFAULT_EXT_DB_SSL_MODE,
    apply_database_mode_to_init_params,
    resolve_init_database_configuration,
)
from ..common import Object, utf8_decode
from ..convert import toxmlstr
from ..clients.common import MultipartForm
from ..exceptions import CTERAException


logger = logging.getLogger('cterasdk.core')


class Setup(BaseCommand):
    """
    Global Admin Setup APIs
    """

    def __init__(self, portal):
        super().__init__(portal)
        self.stage = None

    def _get_current_stage(self):
        status = self.get_setup_status()
        self.stage = status.wizard
        return self.stage

    def init_master(  # pylint: disable=too-many-arguments,too-many-locals
            self,
            name,
            email,
            first_name,
            last_name,
            password,
            domain,
            *,
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
        """
        Initialize the CTERA Portal master server.

        :param str name: User name for the new user
        :param str email: E-mail address of the new user
        :param str first_name: The first name of the new user
        :param str last_name: The last name of the new user
        :param str password: Password for the new user
        :param str domain: The domain suffix for CTERA Portal
        :param str database_mode: ``embedded`` (default) or ``external`` for Enterprise DB
        :param str ext_db_host: External PostgreSQL hostname or VIP (required in external mode)
        :param int ext_db_port: External PostgreSQL port (default 5432)
        :param str ext_db_name: Database name on the external instance (default postgres)
        :param str ext_db_user: External database username (required in external mode)
        :param str ext_db_password: External database password (credentials auth)
        :param str ext_db_auth_method: ``credentials`` (default), ``certificate``, or ``token``
        :param str ext_db_ssl_mode: ``require``, ``verify-ca``, or ``verify-full`` (default verify-full)
        :param str ext_db_ssl_ca_cert: Path or PEM string for the CA certificate
        :param str ext_db_ssl_client_cert: Path or PEM string for the client certificate (certificate auth)
        :param str ext_db_ssl_client_key: Path or PEM string for the client private key (certificate auth)
        """
        self._get_current_stage()

        db_mode, ext_config = resolve_init_database_configuration(
            database_mode=database_mode,
            ext_db_host=ext_db_host,
            ext_db_port=ext_db_port,
            ext_db_name=ext_db_name,
            ext_db_user=ext_db_user,
            ext_db_password=ext_db_password,
            ext_db_auth_method=ext_db_auth_method,
            ext_db_ssl_mode=ext_db_ssl_mode,
            ext_db_ssl_ca_cert=ext_db_ssl_ca_cert,
            ext_db_ssl_client_cert=ext_db_ssl_client_cert,
            ext_db_ssl_client_key=ext_db_ssl_client_key,
        )
        if db_mode == DatabaseMode.External:
            logger.info(
                'Initializing master with external database. %s',
                {
                    'host': ext_db_host,
                    'port': ext_db_port,
                    'database': ext_db_name,
                    'ssl_mode': ext_db_ssl_mode or DEFAULT_EXT_DB_SSL_MODE,
                },
            )

        params = Setup._init_server_params(ServerMode.Master, db_mode, ext_config)
        self._init_server(params, True)

        if self.stage == SetupWizardStage.Portal:
            params = Object()
            params._classname = 'InitParams'  # pylint: disable=protected-access

            params.admin = Object()
            params.admin._classname = 'PortalAdmin'  # pylint: disable=protected-access
            params.admin.name = name
            params.admin.email = email
            params.admin.firstName = first_name
            params.admin.lastName = last_name
            params.admin.password = password

            params.settings = Setup.default_settings()
            params.settings.dnsSuffix = domain
            logger.info('Initializing Portal. %s', {'domain': domain, 'user': name})
            self._core.ctera.execute('/public', 'init', params)
            SetupWizardStatusMonitor(self._core).wait(SetupWizardStage.Portal)
            logger.info('Portal initialized.')
        elif self.stage == SetupWizardStage.Finish:
            logger.warning('Portal already initialized. %s', {'host': self._core.host()})
        self._core.startup.wait()

    def _init_slave(self, ipaddr, secret, database_mode=DatabaseMode.Embedded, ext_config=None):
        self._get_current_stage()
        response = self._core.ctera.execute('/setup/authenticaionMethod', 'askMasterForSlaveAuthenticaionMethod', ipaddr)
        params = Setup._init_server_params(ServerMode.Slave, database_mode, ext_config)
        params.slaveSettings.masterIpAddr = ipaddr
        if response == SlaveAuthenticaionMethod.Password:
            params.slaveSettings.masterPassword = secret
        elif response == SlaveAuthenticaionMethod.PrivateKey:
            params.slaveSettings.masterKey = secret
        else:
            logger.error('Unknown authentication method. %s', {'method': response})
        self._init_server(params, True)

    def _init_server(self, params, wait=False):
        form = MultipartForm()
        if self.stage == SetupWizardStage.Server:
            form.add('inputXml', utf8_decode(toxmlstr(params)))
            form.add('serverMode', params.serverMode)

            if params.serverMode == ServerMode.Slave:
                form.add('masterIpAddr', params.slaveSettings.masterIpAddr)

            logger.info('Initializing server. %s', {'host': self._core.host(), 'mode': params.serverMode})
            self._core.ctera.multipart('/setup', form)
            if wait:
                status = SetupWizardStatusMonitor(self._core).wait(SetupWizardStage.Server)
                self.stage = status.wizard
                logger.info('Server initialized. %s', {'host': self._core.host(), 'mode': params.serverMode})
        else:
            logger.warning('Server already initialized. %s', {'host': self._core.host()})

    def init_application_server(  # pylint: disable=too-many-arguments,too-many-locals
            self,
            ipaddr,
            secret,
            *,
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
        """
        Initialize a CTERA Portal Application Server.

        :param str ipaddr: The CTERA Portal master server IP address
        :param str secret: A password or a PEM-encoded private key for SSH to the master
        :param str database_mode: ``embedded`` (default) or ``external`` for Enterprise DB
        :param str ext_db_host: External PostgreSQL hostname or VIP (required in external mode)
        :param int ext_db_port: External PostgreSQL port (default 5432)
        :param str ext_db_name: Database name on the external instance (default postgres)
        :param str ext_db_user: External database username (required in external mode)
        :param str ext_db_password: External database password (credentials auth)
        :param str ext_db_auth_method: ``credentials`` (default), ``certificate``, or ``token``
        :param str ext_db_ssl_mode: ``require``, ``verify-ca``, or ``verify-full`` (default verify-full)
        :param str ext_db_ssl_ca_cert: Path or PEM string for the CA certificate
        :param str ext_db_ssl_client_cert: Path or PEM string for the client certificate (certificate auth)
        :param str ext_db_ssl_client_key: Path or PEM string for the client private key (certificate auth)
        """
        db_mode, ext_config = resolve_init_database_configuration(
            database_mode=database_mode,
            ext_db_host=ext_db_host,
            ext_db_port=ext_db_port,
            ext_db_name=ext_db_name,
            ext_db_user=ext_db_user,
            ext_db_password=ext_db_password,
            ext_db_auth_method=ext_db_auth_method,
            ext_db_ssl_mode=ext_db_ssl_mode,
            ext_db_ssl_ca_cert=ext_db_ssl_ca_cert,
            ext_db_ssl_client_cert=ext_db_ssl_client_cert,
            ext_db_ssl_client_key=ext_db_ssl_client_key,
        )
        if db_mode == DatabaseMode.External:
            logger.info(
                'Initializing application server with external database. %s',
                {
                    'master': ipaddr,
                    'host': ext_db_host,
                    'port': ext_db_port,
                    'database': ext_db_name,
                    'ssl_mode': ext_db_ssl_mode or DEFAULT_EXT_DB_SSL_MODE,
                },
            )
        self._init_slave(ipaddr, secret, db_mode, ext_config)
        logger.info('Initializing Application Server. %s', {'host': ipaddr})
        self._core.startup.wait()

    @staticmethod
    def _init_server_params(mode, database_mode=DatabaseMode.Embedded, external_database_config=None):
        params = Object()
        params._classname = 'InitServerParams'  # pylint: disable=protected-access
        params.serverMode = mode
        if mode == ServerMode.Slave:
            params.slaveSettings = Object()
            params.slaveSettings._classname = 'SlaveServerSettings'  # pylint: disable=protected-access
        apply_database_mode_to_init_params(params, database_mode, external_database_config)
        return params

    def get_setup_status(self):
        return self._core.ctera.get('/setup/status')

    @staticmethod
    def default_settings():
        settings = Object()
        settings._classname = 'SystemSettings'  # pylint: disable=protected-access
        settings.smtpSettings = Object()
        settings.smtpSettings._classname = 'SMTPSettings'  # pylint: disable=protected-access
        settings.smtpSettings.smtpHost = 'your.mail.server'
        settings.smtpSettings.smtpPort = 25
        settings.smtpSettings.enableTls = False

        settings.defaultPortalSettings = Object()
        settings.defaultPortalSettings._classname = 'PortalSettings'  # pylint: disable=protected-access
        settings.defaultPortalSettings.mailSettings = Object()
        settings.defaultPortalSettings.mailSettings._classname = 'MailSettings'  # pylint: disable=protected-access
        settings.defaultPortalSettings.mailSettings.sender = 'no-reply@your.domain'
        return settings


class SetupWizardStatusMonitor:

    def __init__(self, portal, retries=60, seconds=5):
        self._core = portal
        self._retries = retries
        self._seconds = seconds
        self._attempt = 0

    def wait(self, stage):
        status = None
        current_stage = stage
        while current_stage == stage:
            try:
                self._increment()
                logger.debug('Obtaining wizard status. %s', {'attempt': self._attempt})
                status = self._core.setup.get_setup_status()
                logger.debug('Current wizard status. %s', {
                    'stage': status.wizard,
                    'status': status.currentWizardProgress,
                    'description': status.description
                })
                if status.currentWizardProgress == SetupWizardStatus.Failed:
                    raise CTERAException(f'Initialization failed: {status}')
                current_stage = status.wizard
            except (ConnectionError, TimeoutError) as e:
                logger.debug('Exception. %s', e.__dict__)
        logger.debug('Wizard update. %s', {'previous_stage': stage, 'current_stage': current_stage})
        return status

    def _increment(self):
        self._attempt = self._attempt + 1
        if self._attempt >= self._retries:
            SetupWizardStatusMonitor._unreachable()
        logger.debug('Sleep. %s', {'seconds': self._seconds})
        time.sleep(self._seconds)

    @staticmethod
    def _unreachable():
        logger.error('Timed out. Setup did not complete in a timely manner.')
        raise CTERAException('Timed out. Setup did not complete in a timely manner')
