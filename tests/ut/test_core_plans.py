from unittest import mock

from cterasdk import exception
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
        self._global_admin.get_multi.assert_called_once_with('/plans/' + self._plan_name, mock.ANY)
        expected_include = ['/' + attr for attr in plans.Plans.default]
        actual_include = self._global_admin.get_multi.call_args[0][1]
        self.assertEqual(len(expected_include), len(actual_include))
        for attr in expected_include:
            self.assertIn(attr, actual_include)
        self.assertEqual(ret.name, self._plan_name)

    def test_get_plan_not_found(self):
        get_multi_response = self._get_plan_object(name=None)
        self._init_global_admin(get_multi_response=get_multi_response)
        with self.assertRaises(exception.CTERAException) as error:
            plans.Plans(self._global_admin).get(self._plan_name)
        self._global_admin.get_multi.assert_called_once_with('/plans/' + self._plan_name, mock.ANY)
        expected_include = ['/' + attr for attr in plans.Plans.default]
        actual_include = self._global_admin.get_multi.call_args[0][1]
        self.assertEqual(len(expected_include), len(actual_include))
        for attr in expected_include:
            self.assertIn(attr, actual_include)
        self.assertEqual('Could not find subscription plan', error.exception.message)

    def _get_plan_object(self, **kwargs):
        param = Object()
        param._classname = self._plan_class_name  # pylint: disable=protected-access
        for key, value in kwargs.items():
            setattr(param, key, value)
        return param
