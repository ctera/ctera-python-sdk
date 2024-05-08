from unittest import mock

from cterasdk.exceptions import InputError

from cterasdk import exceptions
from cterasdk.common import Object
from cterasdk.core import plans
from tests.ut import base_core


class TestCorePlans(base_core.BaseCoreTest):

    def setUp(self):
        super().setUp()
        self._plan_class_name = 'Plan'
        self._plan_name = 'Default'

    def test_get_plan_default_attrs(self):
        get_multi_response = self._get_plan_object(name=self._plan_name)
        self._init_global_admin(get_multi_response=get_multi_response)
        ret = plans.Plans(self._global_admin).get(self._plan_name)
        self._global_admin.api.get_multi.assert_called_once_with('/plans/' + self._plan_name, mock.ANY)
        expected_include = ['/' + attr for attr in plans.Plans.default]
        actual_include = self._global_admin.api.get_multi.call_args[0][1]
        self.assertEqual(len(expected_include), len(actual_include))
        for attr in expected_include:
            self.assertIn(attr, actual_include)
        self.assertEqual(ret.name, self._plan_name)

    def test_get_plan_not_found(self):
        get_multi_response = self._get_plan_object(name=None)
        self._init_global_admin(get_multi_response=get_multi_response)
        with self.assertRaises(exceptions.CTERAException) as error:
            plans.Plans(self._global_admin).get(self._plan_name)
        self._global_admin.api.get_multi.assert_called_once_with('/plans/' + self._plan_name, mock.ANY)
        expected_include = ['/' + attr for attr in plans.Plans.default]
        actual_include = self._global_admin.api.get_multi.call_args[0][1]
        self.assertEqual(len(expected_include), len(actual_include))
        for attr in expected_include:
            self.assertIn(attr, actual_include)
        self.assertEqual('Could not find subscription plan', error.exception.message)

    def _test__get_storage_amount(self, new, existing, expected):
        self.assertEqual(plans.Plans._get_storage_amount(new, existing), expected)  # pylint: disable=protected-access

    def test__get_storage_amount_no_value(self):
        self._test__get_storage_amount(None, 100, 100)

    def test__get_storage_amount_int(self):
        self._test__get_storage_amount(50, 100, 50*2**30)

    def test__get_storage_amount_gb(self):
        self._test__get_storage_amount("50GB", 100, 50*2**30)

    def test__get_storage_amount_tb(self):
        self._test__get_storage_amount("50TB", 100, 50*2**40)

    def test__get_storage_amount_pb(self):
        self._test__get_storage_amount("50PB", 100, 50*2**50)

    def test__get_storage_amount_b(self):
        self.assertRaises(InputError, plans.Plans._get_storage_amount, "50B", 100)  # pylint: disable=protected-access

    def test_delete_success(self):
        delete_response = 'Success'
        self._init_global_admin(delete_response=delete_response)
        ret = plans.Plans(self._global_admin).delete(self._plan_name)
        self._global_admin.api.delete.assert_called_once_with(f'/plans/{self._plan_name}')
        self.assertEqual(ret, delete_response)

    def test_delete_failure(self):
        self._global_admin.api.delete = mock.MagicMock(side_effect=exceptions.CTERAException())
        with self.assertRaises(exceptions.CTERAException) as error:
            plans.Plans(self._global_admin).delete(self._plan_name)
        self._global_admin.api.delete.assert_called_once_with(f'/plans/{self._plan_name}')
        self.assertEqual('Plan deletion failed', error.exception.message)

    def test_modify_plan_not_found(self):
        self._init_global_admin()
        self._global_admin.api.get = mock.MagicMock(side_effect=exceptions.CTERAException())
        with self.assertRaises(exceptions.CTERAException) as error:
            plans.Plans(self._global_admin).modify(self._plan_name)
        self._global_admin.api.get.assert_called_once_with(f'/plans/{self._plan_name}')
        self.assertEqual('Could not find subscription plan', error.exception.message)

    def test_modify_update_failure(self):
        self._init_global_admin()
        self._global_admin.api.put = mock.MagicMock(side_effect=exceptions.CTERAException())
        with self.assertRaises(exceptions.CTERAException) as error:
            plans.Plans(self._global_admin).modify(self._plan_name)
        self._global_admin.api.get.assert_called_once_with(f'/plans/{self._plan_name}')
        self._global_admin.api.put.assert_called_once_with(f'/plans/{self._plan_name}', mock.ANY)
        self.assertEqual('Could not modify subscription plan', error.exception.message)

    def test_modify_success_without_apply_changes(self):
        get_response = self._get_plan_object(
            dict(
                retainAll=24,
                hourly=24,
                daily=7,
                weekly=4,
                monthly=12,
                quarterly=0,
                yearly=0,
                retainDeleted=0
            ),
            dict(
                vGateways4=10,
                vGateways8=10,
                appliances=10,
                vGateways32=10,
                vGateways64=10,
                vGateways128=10,
                workstationAgents=10,
                serverAgents=10,
                cloudDrives=10,
                cloudDrivesLite=10,
                storage=1024
            )
        )
        self._init_global_admin(get_response=get_response)
        retention = dict(
            retainAll=12,
            hourly=48,
            daily=30,
            weekly=53,
            monthly=24,
            quarterly=4,
            yearly=7,
            retainDeleted=30
        )
        licenses = dict(
            vGateways4=5,
            vGateways8=5,
            appliances=5,
            vGateways32=5,
            vGateways64=5,
            vGateways128=5,
            workstationAgents=5,
            serverAgents=5,
            cloudDrives=5,
            cloudDrivesLite=5,
            storage=(4096 * (2**30))
        )
        quotas = dict(
            EV4=5,
            EV8=5,
            EV16=5,
            EV32=5,
            EV64=5,
            EV128=5,
            WA=5,
            SA=5,
            Share=5,
            Connect=5,
            Storage=4096
        )
        plans.Plans(self._global_admin).modify(self._plan_name, retention=retention, quotas=quotas, apply_changes=False)
        self._global_admin.api.get.assert_called_once_with(f'/plans/{self._plan_name}')
        self._global_admin.api.put.assert_called_once_with(f'/plans/{self._plan_name}', mock.ANY)
        expected_param = self._get_plan_object(retention, licenses)
        actual_param = self._global_admin.api.put.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)

    def _get_plan_object(self, retention=None, quotas=None, **kwargs):
        plan = Object()
        plan._classname = self._plan_class_name  # pylint: disable=protected-access
        if retention:
            plan.retentionPolicy = Object()
            for key, value in retention.items():
                setattr(plan.retentionPolicy, key, value)
        if quotas:
            for key, value in quotas.items():
                item = Object()
                setattr(item, 'amount', value)
                setattr(plan, key, item)
        for key, value in kwargs.items():
            setattr(plan, key, value)
        return plan
