import logging
from .base_command import BaseCommand
from ..exception import CTERAException
from .enum import PlanItem, PlanRetention
from . import union


class Plans(BaseCommand):
    """
    Global Admin Plan APIs
    """
    default = ['name']

    def _get_entire_object(self, name):
        """
        Get a subscription plan

        :param str name: Name of the subscription plan
        """
        try:
            return self._portal.get('/plans/' + name)
        except CTERAException as error:
            raise CTERAException('Could not find subscription plan', error)

    def get(self, name, include=None):
        """
        Retrieve subscription plan properties

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

    def add(self, name, retention=None, quotas=None):
        """
        Add a subscription plan

        :param dict,optional retention: The data retention policy
        :param dict,optional quotas: The items included in the plan and their respective quota
        """
        plan = self._portal.default_class('Plan')
        plan.name = name
        Plans._assign_retention(plan, retention)
        Plans._assign_quotas(plan, quotas)
        try:
            response = self._portal.add('/plans', plan)
            logging.getLogger().info("Plan created. %s", {'plan': name})
            return response
        except CTERAException as error:
            logging.getLogger().error("Plan creation failed.")
            raise CTERAException('Plan creation failed', error)

    def modify(self, name, retention=None, quotas=None):
        """
        Modify a subscription plan

        :param dict,optional retention: The data retention policy
        :param dict,optional quotas: The items included in the plan and their respective quota
        """
        plan = self._get_entire_object(name)
        Plans._assign_retention(plan, retention)
        Plans._assign_quotas(plan, quotas)
        try:
            response = self._portal.put('/plans/' + name, plan)
            logging.getLogger().info("Plan modified. %s", {'plan': name})
            return response
        except CTERAException as error:
            logging.getLogger().error("Could not modify subscription plan.")
            raise CTERAException('Could not modify subscription plan', error)

    @staticmethod
    def _assign_retention(plan, retention):
        if retention is not None:
            plan.retentionPolicy.retainAll = retention.get(PlanRetention.All, plan.retentionPolicy.retainAll)
            plan.retentionPolicy.hourly = retention.get(PlanRetention.Hourly, plan.retentionPolicy.hourly)
            plan.retentionPolicy.daily = retention.get(PlanRetention.Daily, plan.retentionPolicy.daily)
            plan.retentionPolicy.weekly = retention.get(PlanRetention.Weekly, plan.retentionPolicy.weekly)
            plan.retentionPolicy.monthly = retention.get(PlanRetention.Monthly, plan.retentionPolicy.monthly)
            plan.retentionPolicy.quarterly = retention.get(PlanRetention.Quarterly, plan.retentionPolicy.quarterly)
            plan.retentionPolicy.yearly = retention.get(PlanRetention.Yearly, plan.retentionPolicy.yearly)
            plan.retentionPolicy.retainDeleted = retention.get(PlanRetention.Deleted, plan.retentionPolicy.retainDeleted)

    @staticmethod
    def _assign_quotas(plan, quotas):
        if quotas is not None:
            plan.vGateways4.amount = quotas.get(PlanItem.EV4, plan.vGateways4.amount)
            plan.vGateways8.amount = quotas.get(PlanItem.EV8, plan.vGateways8.amount)
            plan.appliances.amount = quotas.get(PlanItem.EV16, plan.appliances.amount)  # EV16
            plan.vGateways32.amount = quotas.get(PlanItem.EV32, plan.vGateways32.amount)
            plan.vGateways64.amount = quotas.get(PlanItem.EV64, plan.vGateways64.amount)
            plan.vGateways128.amount = quotas.get(PlanItem.EV128, plan.vGateways128.amount)
            plan.workstationAgents.amount = quotas.get(PlanItem.WA, plan.workstationAgents.amount)
            plan.serverAgents.amount = quotas.get(PlanItem.SA, plan.serverAgents.amount)
            plan.cloudDrives.amount = quotas.get(PlanItem.Share, plan.cloudDrives.amount)
            plan.cloudDrivesLite.amount = quotas.get(PlanItem.Connect, plan.cloudDrivesLite.amount)

    def delete(self, name):
        """
        Delete a subscription plan

        :param str username: The name of the subscription plan
        """
        try:
            response = self._portal.delete('/plans/' + name)
            logging.getLogger().info("Plan deleted. %s", {'name': name})
            return response
        except CTERAException as error:
            logging.getLogger().error("Plan deletion failed.")
            raise CTERAException('Plan deletion failed', error)
