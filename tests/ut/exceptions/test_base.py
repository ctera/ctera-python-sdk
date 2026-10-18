import munch
from unittest import mock
from cterasdk import exceptions
from cterasdk.core import admins
from tests.ut import base


class TestExceptions(base.BaseTest):

    def test_reason(self):
        error_message = 'error message'
        error = munch.Munch({
            'response': munch.Munch({
                'error': munch.Munch({
                    'msg': error_message
                })
            })
        })
        self._global_admin.api.get = mock.MagicMock(side_effect=exceptions.transport.InternalServerError(error))
        with self.assertRaises(exceptions.CTERAException) as error:
            admins.Administrators(self._global_admin).modify('user', password='password')
        self.assertEqual(error_message, error.exception.reason)
