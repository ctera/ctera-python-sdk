import logging
import time

from ..exceptions import CTERAException
from ..exceptions.transport import HTTPError
from .base_command import BaseCommand


logger = logging.getLogger('cterasdk.core')


class Startup(BaseCommand):
    """
    Server Startup APIs
    """

    Started = 'Started'

    def status(self):
        """
        Get the server startup status
        """
        response = self._core.ctera.get('/startup')
        return response.status

    def wait(self, retries=120, seconds=5):
        """
        Wait for server startup
        """
        attempt = 0
        while True:
            try:
                if attempt >= retries:
                    logger.error('Timed out. Server did not start in a timely manner.')
                    raise CTERAException('Timed out. Server did not start in a timely manner')
                current_status = self.status()
                if current_status == Startup.Started:
                    logger.info('Server started.')
                    break
                logger.debug('Current server status. %s', {'status': current_status})
                attempt = attempt + 1
                time.sleep(seconds)
            except (ConnectionError, TimeoutError, HTTPError) as e:
                logger.debug('Exception. %s', e.__dict__)
                attempt = attempt + 1
                time.sleep(seconds)
