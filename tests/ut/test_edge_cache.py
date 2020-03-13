from cterasdk.edge import cache
from cterasdk.edge.enum import OperationMode
from tests.ut import base_edge


class TestEdgeCaching(base_edge.BaseEdgeTest):

    def test_enable_caching(self):
        self._init_filer()
        cache.Cache(self._filer).enable()
        self._filer.put.assert_called_once_with('/config/cloudsync/cloudExtender/operationMode', OperationMode.CachingGateway)

    def test_disable_caching(self):
        self._init_filer()
        cache.Cache(self._filer).disable()
        self._filer.put.assert_called_once_with('/config/cloudsync/cloudExtender/operationMode', OperationMode.Disabled)

    def test_force_eviction(self):
        self._init_filer()
        cache.Cache(self._filer).force_eviction()
        self._filer.execute.assert_called_once_with('/config/cloudsync', 'forceExecuteEvictor', None)
