from .base_command import BaseCommand
from ..exception import CTERAException
from . import union


class Plans(BaseCommand):
    """
    Global Admin Plan APIs
    """
    default = ['name']

    def get(self, name, include=None):
        """
        Get a subscription plan

        :param str name: Name of the subscription plan
        :param list[str] include: List of fields to retrieve, defaults to ['name']
        :return: The subscription plan, including the requested fields
        """
        include = union.union(include or [], Plans.default)
        include = ['/' + attr for attr in include]
        plan = self._portal.get_multi('/plans/' + name, include)
        if plan.name is None:
            raise CTERAException('Could not find subscription plan', None, name=name)
        return plan
