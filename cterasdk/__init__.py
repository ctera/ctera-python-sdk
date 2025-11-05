# pylint: disable=wrong-import-position
import cterasdk.settings  # noqa: E402, F401
import cterasdk.exceptions  # noqa: E402, F401

try:
    from . import version
    __version__ = version.__version__
except ImportError:
    __version__ = 'dev'

from .common import Object, PolicyRule  # noqa: E402, F401
from .convert import fromjsonstr, tojsonstr, fromxmlstr, toxmlstr  # noqa: E402, F401
from .core import query  # noqa: E402, F401
from .edge import types as edge_types  # noqa: E402, F401
from .edge import enum as edge_enum  # noqa: E402, F401
from .core import types as core_types  # noqa: E402, F401
from .core import enum as core_enum  # noqa: E402, F401
from .common import types as common_types  # noqa: E402, F401
from .common import enum as common_enum  # noqa: E402, F401
from .objects import GlobalAdmin, ServicesPortal, Edge, Drive, AsyncGlobalAdmin, AsyncServicesPortal, AsyncEdge  # noqa: E402, F401
from . import direct as ctera_direct  # noqa: E402, F401
