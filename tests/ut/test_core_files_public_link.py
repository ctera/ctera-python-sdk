import datetime
from unittest import mock

from cterasdk.core.enum import FileAccessMode
from cterasdk.common import Object
from tests.ut import base_core_services


class BaseCoreServicesFilesPublicLink(base_core_services.BaseCoreServicesTest):

    def setUp(self):
        super().setUp()
        self._path = 'My Files/Documents'
        self._public_link = 'https://cti.ctera.com/invitations/?share=d4db2b6054b7e447e07d&dl=0'

    def test_create_public_link_defaults_args(self):
        execute_response = self._create_public_link_response()
        self._init_services(execute_response=execute_response)
        public_link = self._services.files.create_public_link(self._path)
        self._services.api.execute.assert_called_once_with('', 'createShare', mock.ANY)
        expected_param = self._create_public_link_param(FileAccessMode.RO, 30)
        actual_param = self._services.api.execute.call_args[0][2]
        self._assert_equal_objects(actual_param, expected_param)
        self.assertEqual(public_link, self._public_link)

    def _create_public_link_response(self):
        response = Object()
        response.publicLink = self._public_link
        return response

    def _create_public_link_param(self, access_mode, expire_in):
        param = Object()
        param._classname = 'CreateShareParam'  # pylint: disable=protected-access
        param.url = f'{self._base}/{self._path}'
        param.share = Object()
        param.share._classname = 'ShareConfig'  # pylint: disable=protected-access
        param.share.accessMode = access_mode
        param.share.protectionLevel = 'publicLink'
        param.share.expiration = (datetime.date.today() + datetime.timedelta(days=expire_in)).strftime('%Y-%m-%d')
        param.share.invitee = Object()
        param.share.invitee._classname = 'Collaborator'  # pylint: disable=protected-access
        param.share.invitee.type = 'external'
        return param
