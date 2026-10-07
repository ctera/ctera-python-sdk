from cterasdk.common import Object
from cterasdk.exceptions import CTERAException
from cterasdk.exceptions.transport import InternalServerError
from tests.ut import base


class TestCTERAExceptionReason(base.BaseTest):

    @staticmethod
    def _internal_server_error(portal_error):
        http_error = Object()
        http_error.request = Object(url='https://example/admin/api/administrators/alice')
        http_error.response = Object(status=500, error=portal_error)
        return InternalServerError(http_error)

    def test_reason_returns_portal_msg_from_http_cause(self):
        portal_msg = 'Object validation failed (field: password error: Old and new passwords cannot be the same)'
        portal_error = Object()
        portal_error.msg = portal_msg
        try:
            raise CTERAException('Could not modify user: /administrators/alice') from self._internal_server_error(
                portal_error
            )
        except CTERAException as error:
            self.assertEqual(portal_msg, error.reason)

    def test_reason_is_none_without_cause(self):
        self.assertIsNone(CTERAException('Failed').reason)

    def test_reason_is_none_when_cause_is_not_http_transport_error(self):
        try:
            raise CTERAException('Failed') from ValueError('not transport')
        except CTERAException as error:
            self.assertIsNone(error.reason)

    def test_reason_is_none_when_portal_error_has_no_msg(self):
        try:
            raise CTERAException('Failed') from self._internal_server_error(Object())
        except CTERAException as error:
            self.assertIsNone(error.reason)

    def test_reason_is_none_when_response_error_is_plain_string(self):
        http_error = Object()
        http_error.request = Object(url='https://example/admin')
        http_error.response = Object(status=500, error='Internal Server Error')
        try:
            raise CTERAException('Failed') from InternalServerError(http_error)
        except CTERAException as error:
            self.assertIsNone(error.reason)
