import logging
import time

from ..exceptions import CTERAException, ClientResponseException
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
            response = self._core.ctera.get('/startup')
        except ClientResponseException as error:
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
                    logging.getLogger('cterasdk.core').info('Server started.')
                    break
                logging.getLogger('cterasdk.core').debug('Current server status. %s', {'status': current_status})
                attempt = attempt + 1
                if attempt >= retries:
                    logging.getLogger('cterasdk.core').error('Timed out. Server did not start in a timely manner.')
                    raise CTERAException('Timed out. Server did not start in a timely manner')
                time.sleep(seconds)
            except (ConnectionError, TimeoutError) as e:
                logging.getLogger('cterasdk.core').debug('Exception. %s', e.__dict__)
                attempt = attempt + 1
                time.sleep(seconds)
