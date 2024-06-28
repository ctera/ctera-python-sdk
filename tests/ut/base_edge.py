from unittest import mock

from cterasdk.common import Object
from cterasdk.objects import Edge
from tests.ut import base


class BaseEdgeTest(base.BaseTest):

    def setUp(self):
        super().setUp()
        self._filer = Edge("")

    def _init_filer(self, get_response=None, put_response=None, post_response=None,  # pylint: disable=too-many-arguments
                    form_data_response=None, add_response=None, execute_response=None,
                    delete_response=None, handle_response=None):
        self._filer.api.handle = mock.MagicMock(return_value=handle_response)
        self._filer.api.get = mock.MagicMock(return_value=get_response)
        self._filer.api.put = mock.MagicMock(return_value=put_response)
        self._filer.api.post = mock.MagicMock(return_value=post_response)
        self._filer.api.form_data = mock.MagicMock(return_value=form_data_response)
        self._filer.api.add = mock.MagicMock(return_value=add_response)
        self._filer.api.execute = mock.MagicMock(return_value=execute_response)
        self._filer.api.delete = mock.MagicMock(return_value=delete_response)

    def _init_webdav(self, upload_response=None, mkcol_response=None, copy_response=None, move_response=None, delete_response=None):
        self._filer._ctera_clients = mock.PropertyMock()  # pylint: disable=protected-access
        self._filer._ctera_clients.io = mock.PropertyMock()  # pylint: disable=protected-access
        self._filer._ctera_clients.io.upload = mock.PropertyMock(return_value=upload_response)  # pylint: disable=protected-access
        self._filer._ctera_clients.io.mkdir = mock.PropertyMock(return_value=mkcol_response)  # pylint: disable=protected-access
        self._filer._ctera_clients.io.move = mock.PropertyMock(return_value=move_response)  # pylint: disable=protected-access
        self._filer._ctera_clients.io.copy = mock.PropertyMock(return_value=copy_response)  # pylint: disable=protected-access
        self._filer._ctera_clients.io.delete = mock.PropertyMock(return_value=delete_response)  # pylint: disable=protected-access

    def _init_ctera_migrate(self, get_response=None, put_response=None, post_response=None, delete_response=None):
        self._filer.migrate.get = mock.MagicMock(return_value=get_response)  # pylint: disable=protected-access
        self._filer.migrate.put = mock.MagicMock(return_value=put_response)  # pylint: disable=protected-access
        self._filer.migrate.post = mock.MagicMock(return_value=post_response)  # pylint: disable=protected-access
        self._filer.migrate.delete = mock.MagicMock(return_value=delete_response)  # pylint: disable=protected-access
        self._filer.migrate.login = mock.MagicMock()  # pylint: disable=protected-access

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
