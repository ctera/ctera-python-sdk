from cterasdk.edge import timezone
from tests.ut import base_edge


class TestEdgeTimezone(base_edge.BaseEdgeTest):

    def setUp(self):
        super().setUp()
        self._timezone = '(GMT-05:00) Eastern Time (US , Canada)'

    def test_set_timezone(self):
        self._init_filer()
        timezone.Timezone(self._filer).set_timezone(self._timezone)
        self._filer.put.assert_called_once_with('/config/time/TimeZone', self._timezone)
