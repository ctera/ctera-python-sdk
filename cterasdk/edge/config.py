from datetime import datetime
import logging
import copy

from ..exceptions import CTERAException
from ..convert import fromxmlstr, toxmlstr
from ..common import Device, delete_attrs
from ..lib import FileSystem, TempfileServices
from .base_command import BaseCommand


class Config(BaseCommand):
    """ Edge Filer General Configuration APIs """

    def __init__(self, edge):
        super().__init__(edge)
        self._filesystem = FileSystem.instance()

    def get_location(self):
        """
        Get the location of the Edge Filer

        :return str: The location of the Edge Filer
        """
        return self._edge.api.get('/config/device/location')

    def set_location(self, location):
        """
        Set the location of the Edge Filer

        :param str location: New location to set
        :return str: The new location
        """
        logging.getLogger('cterasdk.edge').info('Configuring device location. %s', {'location': location})
        return self._edge.api.put('/config/device/location', location)

    def get_hostname(self):
        """
        Get the hostname of the Edge Filer

        :return str: The hostname of the Edge Filer
        """
        return self._edge.api.get('/config/device/hostname')

    def set_hostname(self, hostname):
        """
        Set the hostname of the Edge Filer

        :param str hostname: New hostname to set
        :return str: The new hostname
        """
        logging.getLogger('cterasdk.edge').info('Configuring device hostname. %s', {'hostname': hostname})
        return self._edge.api.put('/config/device/hostname', hostname)

    def import_config(self, config, exclude=None):
        """
        Import the Edge Filer configuration

        :param str config: A string or a path to the Edge Filer configuration file
        :param list[str],optional delete_attrs:
         List of configuration properties to exclude from import
        """
        database = None
        if isinstance(config, Device):
            database = copy.deepcopy(config)
        elif isinstance(config, str):
            database = self.load_config(config)

        if exclude:
            delete_attrs(database, exclude)

        path = self._filesystem.join(TempfileServices.mkdir(), f'{self._edge.session().address}.xml')
        self._filesystem.write(path, toxmlstr(database, True).encode('utf-8'))

        return self._import_configuration(path)

    def _import_configuration(self, path):
        self._filesystem.properties(path)
        logging.getLogger('cterasdk.edge').info('Importing Edge Filer configuration.')
        with open(path, 'rb') as fd:
            response = self._edge.api.form_data(
                '/config',
                dict(
                    name='import',
                    type='db',
                    config=fd
                )
            )
            logging.getLogger('cterasdk.edge').info('Imported Edge Filer configuration.')
        return response

    def load_config(self, config):
        """
        Load the Edge Filer configuration

        :param str config: A string or a path to the Edge Filer configuration file
        """
        data = None
        if self._filesystem.exists(config):
            logging.getLogger('cterasdk.edge').info('Reading the Edge Filer configuration from file. %s', {'path': config})
            with open(config, 'r', encoding='utf-8') as f:
                data = f.read()
        else:
            data = config

        database = fromxmlstr(data)
        if database:
            logging.getLogger('cterasdk.edge').info('Completed parsing the Edge Filer configuration. %s', {'firmware': database.firmware})
            return database
        logging.getLogger('cterasdk.edge').error("Failed parsing the Edge Filer's configuration.")
        raise CTERAException("Failed parsing the Edge Filer's configuration")

    def export(self, destination=None):
        """
        Export the Edge Filer configuration

        :param str,optional destination:
         File destination, defaults to the default directory
        """
        default_filename = self._edge.host() + datetime.now().strftime('_%Y-%m-%dT%H_%M_%S') + '.xml'
        directory, filename = self._filesystem.generate_file_location(destination, default_filename)
        logging.getLogger('cterasdk.edge').info('Exporting configuration. %s', {'host': self._edge.host()})
        handle = self._edge.api.handle('/export')
        filepath = FileSystem.instance().save(directory, filename, handle)
        logging.getLogger('cterasdk.edge').info('Exported configuration. %s', {'filepath': filepath})

    def is_wizard_enabled(self):
        """
        Get the current configuration of the first time wizard

        :return bool: True if the first time wizard is enabled, else False
        """
        return self._edge.api.get('/config/gui/openFirstTimeWizard')

    def enable_wizard(self):
        """
        Enable the first time wizard
        """
        return self._set_wizard(True)

    def disable_wizard(self):
        """
        Disable the first time wizard
        """
        return self._set_wizard(False)

    def _set_wizard(self, state):
        logging.getLogger('cterasdk.edge').info('Disabling first time wizard')
        return self._edge.api.put('/config/gui/openFirstTimeWizard', state)
