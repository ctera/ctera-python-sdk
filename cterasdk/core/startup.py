import logging
import time

from ..exception import CTERAException, CTERAClientException, HostUnreachable, ExhaustedException
from .base_command import BaseCommand


class Startup(BaseCommand):
    """
    Server Startup APIs
    """

    Started = 'Started'

    def status(self):
        """
        Get the server startup status
        """
        response = None
        try:
            response = self._portal.get(f'/{self._portal.context}/startup', use_file_url=True)
        except CTERAClientException as error:
            return error.response.body.status
        return response.status

    def wait(self, retries=120, seconds=5):
        """
        Wait for server startup
        """
        attempt = 0
        while True:
            try:
                current_status = self.status()
                if current_status == Startup.Started:
                    logging.getLogger().info('Server started.')
                    break
                logging.getLogger().debug('Current server status. %s', {'status': current_status})
                attempt = attempt + 1
                if attempt >= retries:
                    logging.getLogger().error('Timed out. Server did not start in a timely manner.')
                    raise CTERAException('Timed out. Server did not start in a timely manner')
                time.sleep(seconds)
            except (HostUnreachable, ExhaustedException) as e:
                logging.getLogger().debug('Exception. %s', e.__dict__)
                attempt = attempt + 1
                time.sleep(seconds)
