import copy
from collections.abc import MutableMapping
from aiohttp import TCPConnector, CookieJar, ClientTimeout
import cterasdk.settings
from .tracers import requests, session, postman


class ClientSessionSettings(MutableMapping):

    def __init__(self, *args, **kwargs):
        self._mapping = {
            'connector': {
                '_classname': TCPConnector,
                'ssl': True
            },
            'timeout': {
                '_classname': ClientTimeout,
                'sock_connect': 10,
                'sock_read': 60
            },
            'cookie_jar': {
                '_classname': CookieJar,
                'unsafe': False
            }
        }
        self._mapping.update(dict(*args, **kwargs))

    def update(self, **kwargs):  # pylint: disable=arguments-differ
        for k, v in self._mapping.items():
            attributes = kwargs.get(k, None)
            self._mapping[k] = attributes
            self._mapping[k]['_classname'] = v.get('_classname', None)

    def __getitem__(self, key):
        mapping = copy.deepcopy(self._mapping)
        attributes = mapping.get(key, None)
        new_instance = attributes.pop('_classname', None)
        if new_instance:
            return new_instance(**attributes)
        return attributes

    def __setitem__(self, key, value):
        self._mapping[key] = value

    def __delitem__(self, key):
        del self._mapping[key]

    def __iter__(self):
        return iter(self._mapping)

    def __len__(self):
        return len(self._mapping)

    def __str__(self):
        return str(self._mapping)


class TraceSettings(MutableMapping):

    def __init__(self):
        self._mapping = {
            'trace_configs': [requests.tracer(), session.tracer()]
        }
        if cterasdk.settings.audit.enabled:
            self._mapping['trace_configs'].append(postman.tracer())

    def __getitem__(self, key):
        return self._mapping.get(key, None)

    def __setitem__(self, key, value):  # pylint: disable=useless-parent-delegation
        return super().__setitem__(key, value)

    def __delitem__(self, key):  # pylint: disable=useless-parent-delegation
        return super().__delitem__(key)

    def __len__(self):  # pylint: disable=useless-parent-delegation
        return super().__len__()

    def __iter__(self):
        return iter(self._mapping)
