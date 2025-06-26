from unittest import mock
from urllib.parse import quote

from cterasdk.common import Object
from cterasdk.objects import ServicesPortal
from tests.ut import base


class BaseCoreServicesTest(base.BaseTest):

    def setUp(self):
        super().setUp()
        self._services = ServicesPortal("")
        self._base = '/ServicesPortal/webdav'

    @staticmethod
    def encode_path(path):
        return quote(path)

    def _init_services(self, execute_response=None, form_data_response=None):
        self._services.api.execute = mock.MagicMock(return_value=execute_response)
        self._services.api.form_data = mock.MagicMock(return_value=form_data_response)

    def _create_action_resource_param(self, sources, destinations=None):
        action_resource_param = Object()
        action_resource_param._classname = 'ActionResourcesParam'  # pylint: disable=protected-access
        action_resource_param.urls = []
        for idx, source in enumerate(sources):
            param = Object()
            param._classname = 'SrcDstParam'  # pylint: disable=protected-access
            param.src = f'{self._base}/{source}'
            if destinations:
                param.dest = f'{self._base}/{destinations[idx]}'
            else:
                param.dest = None
            action_resource_param.urls.append(param)
        return action_resource_param
