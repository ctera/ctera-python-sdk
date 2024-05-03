import logging

from .base_command import BaseCommand
from ..common import Object


class Messaging(BaseCommand):
    """
    Portal Messaging Service Management APIs
    """

    def is_active(self):
        """
        Check if messaging service is Active
        """
        return self._core.api.get('/microservices/messaging/globalStatus').status == 'Active'

    def get_status(self):
        """
        Retrieve the global status of messaging service
        """
        res = self._core.api.get('/microservices/messaging/globalStatus')
        return res

    def get_servers_status(self):
        """
        Retrieve the status of the messaging servers
        """
        return {f'{srv.server.name}: "{srv.serverStatus.status}"' for srv in self._core.api.get('/microservices/messaging').currentNodes}

    def add(self, servers):
        """
        Add messaging servers to cluster

        :param list[str] servers: Server names (number of allowed servers: 1 or 3)

        """
        nodes = []
        messaging_obj = self._core.api.get('/microservices/messaging')
        if messaging_obj.globalStatus.canAddServers:
            for node in messaging_obj.availableNodes:
                if node.server.name in servers and node.canAssignAsMessaging.allowed:
                    param = Object()
                    param._class = 'CurrentMessagingNode'  # pylint: disable=protected-access
                    param.server = node.server
                    nodes.append(param)
            if len(nodes) in messaging_obj.globalStatus.validServerNumber:
                response = self._core.api.put('microservices/messaging/currentNodes', nodes)
                logging.getLogger('cterasdk.core').info('Nodes added to cluster successfully')
                return response
            logging.getLogger('cterasdk.core').error('Wrong number of servers. expected:"1" or "3", %s', {'given': len(servers)})
        else:
            logging.getLogger('cterasdk.core').error('Can not add new servers: %s', {messaging_obj.globalStatus.cantAddServersReason})
        return None
