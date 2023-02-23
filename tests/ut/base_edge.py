from unittest import mock

from cterasdk.object import Gateway
from tests.ut import base


class BaseEdgeTest(base.BaseTest):

    def setUp(self):
        super().setUp()
        self._filer = Gateway("")

    def _init_filer(self, get_response=None, put_response=None, post_response=None,  # pylint: disable=too-many-arguments
                    form_data_response=None, add_response=None, execute_response=None,
                    delete_response=None, upload_response=None, openfile_response=None,
                    mkcol_response=None, copy_response=None, move_response=None):
        self._filer.get = mock.MagicMock(return_value=get_response)
        self._filer.put = mock.MagicMock(return_value=put_response)
        self._filer.post = mock.MagicMock(return_value=post_response)
        self._filer.form_data = mock.MagicMock(return_value=form_data_response)
        self._filer.add = mock.MagicMock(return_value=add_response)
        self._filer.execute = mock.MagicMock(return_value=execute_response)
        self._filer.delete = mock.MagicMock(return_value=delete_response)
        self._filer.upload = mock.MagicMock(return_value=upload_response)
        self._filer.openfile = mock.MagicMock(return_value=openfile_response)
        self._filer.mkcol = mock.MagicMock(return_value=mkcol_response)
        self._filer.copy = mock.MagicMock(return_value=copy_response)
        self._filer.move = mock.MagicMock(return_value=move_response)

    def _init_ctera_migrate(self, get_response=None, put_response=None, post_response=None, delete_response=None):
        self._filer._ctera_migrate.get = mock.MagicMock(return_value=get_response)  # pylint: disable=protected-access
        self._filer._ctera_migrate.put = mock.MagicMock(return_value=put_response)  # pylint: disable=protected-access
        self._filer._ctera_migrate.post = mock.MagicMock(return_value=post_response)  # pylint: disable=protected-access
        self._filer._ctera_migrate.delete = mock.MagicMock(return_value=delete_response)  # pylint: disable=protected-access
        self._filer._ctera_migrate.login = mock.MagicMock()  # pylint: disable=protected-access
