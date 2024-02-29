from unittest import mock

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
        self._filer.webdav.upload = mock.MagicMock(return_value=upload_response)
        self._filer.webdav.mkcol = mock.MagicMock(return_value=mkcol_response)
        self._filer.webdav.copy = mock.MagicMock(return_value=copy_response)
        self._filer.webdav.move = mock.MagicMock(return_value=move_response)
        self._filer.webdav.delete = mock.MagicMock(return_value=delete_response)

    def _init_ctera_migrate(self, get_response=None, put_response=None, post_response=None, delete_response=None):
        self._filer.migrate.get = mock.MagicMock(return_value=get_response)  # pylint: disable=protected-access
        self._filer.migrate.put = mock.MagicMock(return_value=put_response)  # pylint: disable=protected-access
        self._filer.migrate.post = mock.MagicMock(return_value=post_response)  # pylint: disable=protected-access
        self._filer.migrate.delete = mock.MagicMock(return_value=delete_response)  # pylint: disable=protected-access
        self._filer.migrate.login = mock.MagicMock()  # pylint: disable=protected-access
