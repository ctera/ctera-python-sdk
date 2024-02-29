from .base_command import BaseCommand


class Domains(BaseCommand):
    """
    Portal Domains Management APIs
    """

    def list_domains(self):
        """
        List all domains

        :return list: List of all domains
        """
        return self._core.api.get('/domains')
