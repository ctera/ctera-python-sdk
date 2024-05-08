from unittest import mock

from cterasdk.common import Object
from cterasdk.objects import GlobalAdmin
from tests.ut import base


class BaseCoreTest(base.BaseTest):

    def setUp(self):
        super().setUp()
        self._global_admin = GlobalAdmin("")

    def _init_global_admin(self, get_response=None, get_multi_response=None, put_response=None,
                           execute_response=None, form_data_response=None, add_response=None,
                           delete_response=None):
        self._global_admin.api.get = mock.MagicMock(return_value=get_response)
        self._global_admin.api.get_multi = mock.MagicMock(return_value=get_multi_response)
        self._global_admin.api.put = mock.MagicMock(return_value=put_response)
        self._global_admin.api.execute = mock.MagicMock(return_value=execute_response)
        self._global_admin.api.form_data = mock.MagicMock(return_value=form_data_response)
        self._global_admin.api.add = mock.MagicMock(return_value=add_response)
        self._global_admin.api.delete = mock.MagicMock(return_value=delete_response)

    def _init_setup(self, get_response=None, execute_response=None, multipart_response=None):
        self._global_admin.ctera.get = mock.MagicMock(return_value=get_response)
        self._global_admin.ctera.execute = mock.MagicMock(return_value=execute_response)
        self._global_admin.ctera.multipart = mock.MagicMock(return_value=multipart_response)

    @staticmethod
    def enable_tenant_context(m):
        m().in_tenant_context.return_value = True

    @staticmethod
    def disable_tenant_context(m):
        m().in_tenant_context.return_value = False

    @staticmethod
    def _create_filter(filter_type, field, restriction, value):
        query_filter = Object()
        query_filter._classname = filter_type  # pylint: disable=protected-access
        query_filter.field = field
        query_filter.restriction = restriction
        query_filter.value = value
        return query_filter

    @staticmethod
    def _create_query_params(include_classname=False, start_from=None,
                             count_limit=None, include=None, filters=None,
                             or_filter=None, all_portals=None, **kwargs):
        query_params = Object()

        if include_classname:
            query_params._classname = 'QueryParams'  # pylint: disable=protected-access
        if start_from is not None:
            query_params.startFrom = start_from
        if count_limit is not None:
            query_params.countLimit = count_limit
        if include is not None:
            query_params.include = include
        if filters is not None:
            query_params.filters = filters
        if or_filter is not None:
            query_params.orFilter = or_filter
        if all_portals is not None:
            query_params.allPortals = all_portals

        for k, v in kwargs.items():
            setattr(query_params, k, v)

        return query_params
