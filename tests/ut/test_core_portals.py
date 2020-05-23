from unittest import mock

from cterasdk.common import Object
from cterasdk.core.enum import PortalType
from cterasdk.core import portals
from cterasdk.core import query
from tests.ut import base_core


class TestCorePortals(base_core.BaseCoreTest):

    _tenants_first_page = ['a', 'b', 'c', 'd']
    _tenants_second_page = ['e', 'f', 'g', 'h']

    def setUp(self):
        super().setUp()
        self._name = 'acme'
        self._plan_name = 'plan name'
        self._plan_ref = 'plan ref'
        self._display_name = 'Acme Corp.'
        self._billing_id = 'billing-id'
        self._company = 'The Acme Corporation'

    @staticmethod
    def _get_query_portals_response(execute_path, execute_name, execute_param):
        # pylint: disable=unused-argument
        query_response = Object()
        tenants = None
        if execute_param.startFrom == 0:
            query_response.hasMore = True
            tenants = TestCorePortals._tenants_first_page
        else:
            query_response.hasMore = False
            tenants = TestCorePortals._tenants_second_page
        query_response.objects = []
        for tenant in tenants:
            tenant_param = Object()
            tenant_param.name = tenant
            query_response.objects.append(tenant_param)
        return query_response

    def test_list_team_portals(self):
        self._test_list_tenants(PortalType.Team)

    def test_list_reseller_portals(self):
        self._test_list_tenants(PortalType.Reseller)

    def _test_list_tenants(self, portal_type=None):
        with mock.patch("cterasdk.core.devices.query.iterator") as query_iterator_mock:
            portals.Portals(self._global_admin).list_tenants(portal_type=portal_type)
            path = TestCorePortals._get_list_tenants_urlpath(portal_type)
            query_iterator_mock.assert_called_once_with(self._global_admin, path, mock.ANY)
            expected_param = self._get_expected_list_portals_params()
            actual_param = query_iterator_mock.call_args[0][2]
            self._assert_equal_objects(actual_param, expected_param)

    @staticmethod
    def _get_list_tenants_urlpath(portal_type):
        path = '/portals'
        if portal_type == PortalType.Team:
            path = '/teamPortals'
        elif portal_type == PortalType.Reseller:
            path = '/resellerPortals'
        return path

    @staticmethod
    def _get_expected_list_portals_params():
        builder = query.QueryParamBuilder().include(portals.Portals.default)
        return builder.build()

    def test_get_active_tenants(self):
        self._global_admin.execute = mock.MagicMock(side_effect=TestCorePortals._get_query_portals_response)
        tenant_objects = portals.Portals(self._global_admin).tenants()

        tenant_names = TestCorePortals._tenants_first_page + TestCorePortals._tenants_second_page
        counter = 0
        for tenant_object in tenant_objects:
            self.assertEqual(tenant_names[counter], tenant_object.name)
            counter = counter + 1

        self._global_admin.execute.assert_has_calls(
            [
                mock.call('', 'getPortalsDisplayInfo', mock.ANY),
                mock.call('', 'getPortalsDisplayInfo', mock.ANY)
            ]
        )

    def test_add_tenant_default_args(self):
        add_response = 'Success'
        self._init_global_admin(add_response=add_response)
        ret = portals.Portals(self._global_admin).add(self._name)
        self._global_admin.add.assert_called_once_with('/teamPortals', mock.ANY)
        expected_param = self._get_portal_param()
        actual_param = self._global_admin.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, add_response)

    def test_add_tenant_with_display_name_with_billing_id_with_company(self):
        add_response = 'Success'
        self._init_global_admin(add_response=add_response)
        ret = portals.Portals(self._global_admin).add(self._name, self._display_name, self._billing_id, self._company)
        self._global_admin.add.assert_called_once_with('/teamPortals', mock.ANY)
        expected_param = self._get_portal_param(self._display_name, self._billing_id, self._company)
        actual_param = self._global_admin.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, add_response)

    def test_add_tenant_with_plan(self):
        add_response = 'Success'
        get_multi_response = TestCorePortals._get_plan_object(self._plan_name, self._plan_ref)
        self._init_global_admin(get_multi_response=get_multi_response, add_response=add_response)
        ret = portals.Portals(self._global_admin).add(self._name, plan=self._plan_name)
        self._global_admin.add.assert_called_once_with('/teamPortals', mock.ANY)
        expected_param = self._get_portal_param(plan=self._plan_ref)
        actual_param = self._global_admin.add.call_args[0][1]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(ret, add_response)

    @staticmethod
    def _get_plan_object(plan_name, plan_ref):
        param = Object()
        param.name = plan_name
        param.baseObjectRef = plan_ref
        return param

    def test_subscribe(self):
        execute_response = 'Success'
        self._init_global_admin(execute_response=execute_response)
        ret = portals.Portals(self._global_admin).subscribe(self._name, self._plan_name)
        self._global_admin.execute.assert_called_once_with('/portals/' + self._name, 'subscribe', self._plan_name)
        self.assertEqual(ret, execute_response)

    def test_delete_portal(self):
        execute_response = 'Success'
        self._init_global_admin(execute_response=execute_response)
        ret = portals.Portals(self._global_admin).delete(self._name)
        self._global_admin.execute.assert_called_once_with('/teamPortals/' + self._name, 'delete')
        self.assertEqual(ret, execute_response)

    def test_undelete_portal(self):
        execute_response = 'Success'
        self._init_global_admin(execute_response=execute_response)
        ret = portals.Portals(self._global_admin).undelete(self._name)
        self._global_admin.execute.assert_called_once_with('/teamPortals/' + self._name, 'moveFromTrashcan')
        self.assertEqual(ret, execute_response)

    def test_browse_tenant(self):
        self._init_global_admin()
        portals.Portals(self._global_admin).browse(self._name)
        self._global_admin.put.assert_called_once_with('/currentPortal', self._name)

    def test_browse_global_admin(self):
        self._init_global_admin()
        portals.Portals(self._global_admin).browse_global_admin()
        self._global_admin.put.assert_called_once_with('/currentPortal', '')

    def _get_portal_param(self, display_name=None, billing_id=None, company=None, comment=None, plan=None):
        param = Object()
        param._classname = 'TeamPortal'  # pylint: disable=protected-access
        param.name = self._name
        param.displayName = display_name
        param.externalPortalId = billing_id
        param.companyName = company
        param.comment = comment
        if plan:
            param.plan = plan
        return param
