import logging
from .base_command import BaseCommand
from ..exceptions import CTERAException, InputError, ObjectNotFoundException
from .enum import PlanItem, PlanRetention
from ..common import union, convert_size, DataUnit, PolicyRuleConverter
from . import query


class Plans(BaseCommand):
    """
    Portal Plan APIs

    :ivar cterasdk.core.plans.PlanAutoAssignPolicy auto_assign: Object holding the Portal subscription plan auto assignment rules APIs
    """
    default = ['name']
    _allowed_storage_size_units = [DataUnit.GB, DataUnit.TB, DataUnit.PB]

    def __init__(self, portal):
        super().__init__(portal)
        self.auto_assign = PlanAutoAssignPolicy(self._core)

    def _get_entire_object(self, name):
        """
        Get a subscription plan

        :param str name: Name of the subscription plan
        """
        try:
            return self._core.api.get('/plans/' + name)
        except CTERAException as error:
            raise CTERAException('Could not find subscription plan', error)

    def by_name(self, names, include=None):
        """
        Get Plans by their names

        :param list[str],optional names: List of names of plans
        :param list[str],optional include: List of fields to retrieve, defaults to ['name']
        :param list[cterasdk.core.query.FilterBuilder],optional filters: List of additional filters, defaults to None

        :return: Iterator for all matching Plans
        :rtype: cterasdk.lib.iterator.Iterator
        """
        filters = [query.FilterBuilder('name').eq(name) for name in names]
        return self.list_plans(include, filters)

    def list_plans(self, include=None, filters=None):
        """
        List Plans

        :param list[str],optional include: List of fields to retrieve, defaults to ['name']
        :param list[],optional filters: List of additional filters, defaults to None

        :return: Iterator for all matching Plans
        :rtype: cterasdk.lib.iterator.Iterator
        """
        include = union(include or [], Plans.default)
        builder = query.QueryParamBuilder().include(include)
        filters = filters or []
        for query_filter in filters:
            builder.addFilter(query_filter)
        builder.orFilter((len(filters) > 1))
        param = builder.build()
        yield from query.iterator(self._core, '/plans', param)

    def get(self, name, include=None):
        """
        Retrieve subscription plan properties

        :param str name: Name of the subscription plan
        :param list[str] include: List of fields to retrieve, defaults to ['name']
        :return: The subscription plan, including the requested fields
        """
        include = union(include or [], Plans.default)
        include = ['/' + attr for attr in include]
        plan = self._core.api.get_multi('/plans/' + name, include)
        if plan.name is None:
            raise ObjectNotFoundException('Could not find subscription plan', f'/plans/{name}', name=name)
        return plan

    def add(self, name, services=None, retention=None, quotas=None):
        """
        Add a subscription plan

        :param dict,optional services: Services to enable or disable
        :param dict,optional retention: The data retention policy
        :param dict,optional quotas: The items included in the plan and their respective quota
        """
        plan = self._core.api.defaults('Plan')
        plan.name = name
        Plans._assign_services(plan, services)
        Plans._assign_retention(plan, retention)
        Plans._assign_quotas(plan, quotas)
        try:
            response = self._core.api.add('/plans', plan)
            logging.getLogger('cterasdk.core').info("Plan created. %s", {'plan': name})
            return response
        except CTERAException as error:
            logging.getLogger('cterasdk.core').error("Plan creation failed.")
            raise CTERAException('Plan creation failed', error)

    def modify(self, name, services=None, retention=None, quotas=None, apply_changes=True):
        """
        Modify a subscription plan

        :param dict,optional services: Services to enable or disable
        :param dict,optional retention: The data retention policy
        :param dict,optional quotas: The items included in the plan and their respective quota
        :param bool,optional apply_changes: Apply provisioning changes immediately
        """
        plan = self._get_entire_object(name)
        Plans._assign_services(plan, services)
        Plans._assign_retention(plan, retention)
        Plans._assign_quotas(plan, quotas)
        try:
            response = self._core.api.put('/plans/' + name, plan)
            logging.getLogger('cterasdk.core').info("Plan modified. %s", {'plan': name})
            if apply_changes:
                if self._core.session().in_tenant_context():
                    self._core.users.apply_changes(True)
                else:
                    self._core.portals.apply_changes(True)
            return response
        except CTERAException as error:
            logging.getLogger('cterasdk.core').error("Could not modify subscription plan.")
            raise CTERAException('Could not modify subscription plan', error)

    @staticmethod
    def _assign_services(plan, services):
        if services is not None:
            for service in plan.services:
                service_state = services.get(service.serviceName, None)
                if service_state:
                    service.serviceState = service_state

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
            plan.storage.amount = Plans._get_storage_amount(quotas.get(PlanItem.Storage), plan.storage.amount)

    @staticmethod
    def _get_storage_amount(new_amount, existing_amount):
        if new_amount is None:
            return existing_amount

        unit = DataUnit.GB
        if isinstance(new_amount, int):
            value = new_amount
        elif isinstance(new_amount, str):
            try:
                value = int(new_amount)
            except ValueError:
                value = int(new_amount[:-2])
                unit = new_amount[-2:]
        else:
            raise InputError("Invalid storage amount type", new_amount, ['int', 'str'])

        if unit not in Plans._allowed_storage_size_units:
            raise InputError("Invalid unit type", unit, Plans._allowed_storage_size_units)

        return convert_size(value, unit, DataUnit.B)

    def delete(self, name):
        """
        Delete a subscription plan

        :param str username: The name of the subscription plan
        """
        try:
            response = self._core.api.delete('/plans/' + name)
            logging.getLogger('cterasdk.core').info("Plan deleted. %s", {'name': name})
            return response
        except CTERAException as error:
            logging.getLogger('cterasdk.core').error("Plan deletion failed.")
            raise CTERAException('Plan deletion failed', error)


class PlanAutoAssignPolicy(BaseCommand):

    def get_policy(self):
        """
        Get plans auto assignment policy
        """
        return self._core.api.execute('', 'getPlanAutoAssignmentRules')

    def set_policy(self, rules, apply_default=None, default=None, apply_changes=True):
        """
        Set plans auto assignment policy

        :param list[cterasdk.common.types.PolicyRule] rules: List of policy rules
        :param bool,optional apply_default: If no match found, apply default plan. If not passed, the current config will be kept
        :param str,optional default: Name of a plan to assign if no match found. Ignored unless the ``apply_default`` is set to ``True``
        :param bool,optional apply_changes: Apply provisioning changes upon update, defaults to ``True``
        """
        plans = {rule.assignment for rule in rules}
        if default:
            plans.add(default)
        plans = list(plans)
        portal_plans = {plan.name: plan for plan in self._core.plans.by_name(plans, ['baseObjectRef'])}

        not_found = [plan for plan in plans if plan not in portal_plans.keys()]
        if not_found:
            logging.getLogger('cterasdk.core').error('Could not find one or more plans. %s', {'plans': not_found})
            raise CTERAException('Could not find one or more plans', None, plans=not_found)

        policy = self.get_policy()

        if apply_default is False:
            policy.defaultPlan = None
        elif apply_default is True and default:
            policy.defaultPlan = portal_plans.get(default).baseObjectRef

        policy_rules = [PolicyRuleConverter.convert(rule, 'PlanAutoAssignmentRule', 'plan',
                        portal_plans.get(rule.assignment).baseObjectRef) for rule in rules]
        policy.planAutoAssignmentRules = policy_rules

        response = self._core.api.execute('', 'setPlanAutoAssignmentRules', policy)
        logging.getLogger('cterasdk.core').info('Set plans auto assignment rules.')

        if apply_changes:
            self._core.users.apply_changes(True)

        return response
