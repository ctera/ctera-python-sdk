import logging

from ..common import union, Object
from .base_command import BaseCommand
from .types import ScheduledTask, BackgroundTask
from . import query
from ..exceptions import CTERAException, ObjectNotFoundException


class Servers(BaseCommand):
    """
    Global Admin Servers APIs
    """

    default = ['name']

    def __init__(self, portal):
        super().__init__(portal)
        self.tasks = Tasks(self._core)

    def _get_entire_object(self, server):
        try:
            return self._core.api.get(f'/servers/{server}')
        except CTERAException as error:
            raise CTERAException('Failed to retrieve server', error)

    def get(self, name, include=None):
        """
        Retrieve server properties

        :param str name: Name of the server
        :param list[str] include: List of fields to retrieve, defaults to ['name']
        :return: The server, including the requested fields
        """
        include = union(include or [], Servers.default)
        include = ['/' + attr for attr in include]
        server = self._core.api.get_multi(f'/servers/{name}', include)
        if server.name is None:
            raise ObjectNotFoundException('Could not find server', f'/servers/{name}', name=name)
        return server

    def list_servers(self, include=None):
        """
        Retrieve the servers that comprise CTERA Portal.\n
        To retrieve servers, you must first browse the Global Administration Portal, using: `GlobalAdmin.portals.browse_global_admin()`

        :param list[str],optional include: List of fields to retrieve, defaults to ['name']
        """
        # browse administration
        include = union(include or [], Servers.default)
        param = query.QueryParamBuilder().include(include).build()
        return query.iterator(self._core, '/servers', param)

    def modify(self, name, server_name=None, app=None, preview=None, enable_public_ip=None, public_ip=None,
               allow_user_login=None, enable_replication=None, replica_of=None):
        """
        Modify a Portal server

        :param str name: The current server name
        :param str,optional server_name: New server name
        :param bool,optional app: Application server
        :param bool,optional preview: Preview server
        :param bool,optional enable_public_ip: Enable or disable public NAT address
        :param str,optional public_ip: Public NAT address
        :param bool,optional allow_user_login: Allow or disallow logins to this server
        :param bool,optional enable_replication: Enable or disable database replication
        :param str,optional replica_of: Configure as a replicate of another Portal server. `enable_replication` must be set to `True`
        """

        server = self._get_entire_object(name)
        if enable_replication is True and replica_of is not None:
            server.replicationSettings = Object()
            server.replicationSettings._classname = 'ServerReplicationSettings'  # pylint: disable=protected-access
            server.replicationSettings.replicationOf = self.get(replica_of, ['baseObjectRef']).baseObjectRef
        if enable_replication is False:
            server.replicationSettings = None
        if server_name is not None:
            server.name = server_name
        if app is not None:
            server.isApplicationServer = app
        if preview is not None:
            server.renderingServer = preview
        if enable_public_ip is True and public_ip is not None:
            server.publicIpaddr = public_ip
        elif enable_public_ip is False:
            server.publicIpaddr = None
        if allow_user_login is not None:
            server.allowUserLogin = allow_user_login

        try:
            response = self._core.api.put(f'/servers/{name}', server)
            logging.getLogger('cterasdk.core').info("Server modified. %s", {'server': name})
            return response
        except CTERAException as error:
            logging.getLogger('cterasdk.core').error("Could not modify server.")
            raise CTERAException('Could not modify server', error)


class Tasks(BaseCommand):

    def background(self, name):
        """
        Get all background tasks

        :param str name: Name of the server
        :return: List of tasks
        """
        return [BackgroundTask.from_server_object(task, f'servers/{name}/bgTasks/{task.id}')
                for task in self._core.api.get(f'/servers/{name}/bgTasks')]

    def scheduled(self, name):
        """
        Get all scheduled tasks

        :param str name: Name of the server
        :return: List of tasks
        """
        return [ScheduledTask.from_server_object(task) for task in self._core.api.get(f'/servers/{name}/schedTasks')]
