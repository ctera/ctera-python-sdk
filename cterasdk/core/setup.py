import logging
import time
import re

from .base_command import BaseCommand
from .enum import ServerMode, SetupWizardStage, SetupWizardStatus, SlaveAuthenticaionMethod
from ..common import Object, utf8_decode
from ..convert import toxmlstr
from ..clients.common import MultipartForm
from ..exceptions import CTERAException


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

    def init_master(self, name, email, first_name, last_name, password, domain):
        """
        Initialize the CTERA Portal master server.

        :param str name: User name for the new user
        :param str email: E-mail address of the new user
        :param str first_name: The first name of the new user
        :param str last_name: The last name of the new user
        :param str password: Password for the new user
        :param str domain: The domain suffix for CTERA Portal
        """
        self._get_current_stage()

        params = Setup._init_server_params(ServerMode.Master)
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
            logging.getLogger('cterasdk.core').info('Initializing Portal. %s', {'domain': domain, 'user': name})
            self._core.ctera.execute('/public', 'init', params)
            SetupWizardStatusMonitor(self._core).wait(SetupWizardStage.Portal)
            logging.getLogger('cterasdk.core').info('Portal initialized.')
        elif self.stage == SetupWizardStage.Finish:
            logging.getLogger('cterasdk.core').warning('Portal already initialized. %s', {'host': self._core.host()})
        self._core.startup.wait()

    def _init_slave(self, ipaddr, secret):
        self._get_current_stage()
        response = self._core.ctera.execute('/setup/authenticaionMethod', 'askMasterForSlaveAuthenticaionMethod', ipaddr)
        params = Setup._init_server_params(ServerMode.Slave)
        params.slaveSettings.masterIpAddr = ipaddr
        if response == SlaveAuthenticaionMethod.Password:
            params.slaveSettings.masterPassword = secret
        elif response == SlaveAuthenticaionMethod.PrivateKey:
            params.slaveSettings.masterKey = secret
        else:
            logging.getLogger('cterasdk.core').error('Unknown authentication method. %s', {'method': response})
        self._init_server(params, True)

    def _init_server(self, params, wait=False):
        form = MultipartForm()
        if self.stage == SetupWizardStage.Server:
            form.add('inputXml', utf8_decode(toxmlstr(params)))
            form.add('serverMode', params.serverMode)

            if params.serverMode == ServerMode.Slave:
                form.add('masterIpAddr', params.slaveSettings.masterIpAddr)

            logging.getLogger('cterasdk.core').info('Initializing server. %s', {'host': self._core.host(), 'mode': params.serverMode})
            self._core.ctera.multipart('/setup', form)
            if wait:
                status = SetupWizardStatusMonitor(self._core).wait(SetupWizardStage.Server)
                self.stage = status.wizard
                logging.getLogger('cterasdk.core').info('Server initialized. %s', {'host': self._core.host(), 'mode': params.serverMode})
        else:
            logging.getLogger('cterasdk.core').warning('Server already initialized. %s', {'host': self._core.host()})

    def init_application_server(self, ipaddr, secret):
        """
        Initialize a CTERA Portal Application Server.

        :param str ipaddr: The CTERA Portal master server IP address
        :param str secret: A password or a PEM-encoded private key
        """
        self._init_slave(ipaddr, secret)
        if self.stage == SetupWizardStage.Replication:
            logging.getLogger('cterasdk.core').info('Initializing an Application Server. %s', {'host': ipaddr})
            params = Setup._init_replication_param()
            self._init_role(params)
        self._core.startup.wait()

    def init_replication_server(self, ipaddr, secret, replicate_from=None):
        """
        Initialize a CTERA Portal Database Replication Server.

        :param str ipaddr: The CTERA Portal master server IP address
        :param str secret: A password or a PEM-encoded private key
        :param str replicate_from: The name of a CTERA Portal server to replicate from
        """
        self._init_slave(ipaddr, secret)
        if self.stage == SetupWizardStage.Replication:
            logging.getLogger('cterasdk.core').info('Initializing a Replication Database Server. %s',
                                                    {'host': ipaddr, 'replicate_from': replicate_from})
            logging.getLogger('cterasdk.core').debug('Retrieving database replication candidates.')
            replication_candidates = {re.search('([^/]+$)', k).group(0): k for k in self.get_replication_candidates()}
            if replication_candidates:
                if replicate_from is None and len(replication_candidates) == 1:
                    server = next(iter(replication_candidates.values()))
                else:
                    server = replication_candidates.get(replicate_from)
                if server:
                    logging.getLogger('cterasdk.core').debug('Found server in replication candidates. %s', {'server': replicate_from})
                    params = Setup._init_replication_param(server)
                    self._init_role(params)
                else:
                    logging.getLogger('cterasdk.core').error('Could not find database replication target. %s', {
                        'target': replicate_from,
                        'options': replication_candidates
                    })
                    raise CTERAException('Could not find database replication target.',
                                         None, target=replicate_from, options=replication_candidates)
            else:
                logging.getLogger('cterasdk.core').error('Could not find database replication candidates.')
        self._core.startup.wait()

    def _init_role(self, params):
        response = self._core.ctera.execute('/public/servers', 'setReplication', params)
        status = SetupWizardStatusMonitor(self._core).wait(SetupWizardStage.Replication)
        self.stage = status.wizard
        return response

    def get_replication_candidates(self):
        return self._core.ctera.execute('/public/servers', 'getReplicaitonCandidates', None)

    @staticmethod
    def _init_replication_param(replicate_from=None):
        params = Object()
        params._classname = 'SetReplicationParam'  # pylint: disable=protected-access
        if replicate_from:
            params.enabledReplicationParam = Object()
            params.enabledReplicationParam._classname = 'EnabledReplicationParam'  # pylint: disable=protected-access
            params.enabledReplicationParam.replicationOf = replicate_from
            params.enabledReplicationParam.restartDB = True
        return params

    @staticmethod
    def _init_server_params(mode):
        params = Object()
        params._classname = 'InitServerParams'  # pylint: disable=protected-access
        params.serverMode = mode
        if mode == ServerMode.Slave:
            params.slaveSettings = Object()
            params.slaveSettings._classname = 'SlaveServerSettings'  # pylint: disable=protected-access
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
                logging.getLogger('cterasdk.core').debug('Obtaining wizard status. %s', {'attempt': self._attempt})
                status = self._core.setup.get_setup_status()
                logging.getLogger('cterasdk.core').debug('Current wizard status. %s', {
                    'stage': status.wizard,
                    'status': status.currentWizardProgress,
                    'description': status.description
                })
                if status.currentWizardProgress == SetupWizardStatus.Failed:
                    raise CTERAException('Initialization failed.', status)
                current_stage = status.wizard
            except (ConnectionError, TimeoutError) as e:
                logging.getLogger('cterasdk.core').debug('Exception. %s', e.__dict__)
        logging.getLogger('cterasdk.core').debug('Wizard update. %s', {'previous_stage': stage, 'current_stage': current_stage})
        return status

    def _increment(self):
        self._attempt = self._attempt + 1
        if self._attempt >= self._retries:
            SetupWizardStatusMonitor._unreachable()
        logging.getLogger('cterasdk.core').debug('Sleep. %s', {'seconds': self._seconds})
        time.sleep(self._seconds)

    @staticmethod
    def _unreachable():
        logging.getLogger('cterasdk.core').error('Timed out. Setup did not complete in a timely manner.')
        raise CTERAException('Timed out. Setup did not complete in a timely manner')
