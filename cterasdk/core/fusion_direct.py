"""
Fusion Direct cloud folder API payload builders.

Schema ``_classname`` values remain ``OpenFabricS3DataStorage`` and ``OpenFabricSettings`` (portal legacy names).
"""

from .enum import OpenFabricStorageMode
from ..common import Object


# Default when ``storage`` is omitted; matches portal ``LocationsType.GenericS3`` name.
DEFAULT_FUSION_DIRECT_S3_STORAGE = 'GenericS3'
DEFAULT_OPEN_FABRIC_S3_STORAGE = DEFAULT_FUSION_DIRECT_S3_STORAGE  # legacy alias

# Matches portal ``com.ctera.infra.dataset.SimpleType.DONT_CHANGE_PASSWORD`` for ``dataStorage.secretKey``
# on :meth:`cterasdk.core.cloudfs.CloudDrives.modify` when the secret should stay unchanged.
FUSION_DIRECT_SECRET_KEY_UNCHANGED = "*****DON'T CHANGE*****"


class OpenFabricS3DataStorageBuilder:
    """
    Build ``OpenFabricS3DataStorage`` for ``OpenFabricSettings.dataStorage`` (Fusion Direct).

    The ``storage`` value must be a ``LocationsType`` enum name accepted by the portal
    for Fusion Direct (for example ``GenericS3``, ``S3``, ``MinIOS3``). When omitted,
    ``GenericS3`` is used, consistent with portal resolution of blank storage.
    """

    def __init__(self, bucket, access_key, secret_key, end_point, *, storage=None, use_https=True,
                 region=None, trust_all_certificates=False, use_path_style_addressing=False,
                 sqs_url=None, metadata_tags=False):
        self._bucket = bucket
        self._access_key = access_key
        self._secret_key = secret_key
        self._end_point = end_point
        self._storage = storage if storage is not None else DEFAULT_FUSION_DIRECT_S3_STORAGE
        self._use_https = use_https
        self._region = region
        self._trust_all_certificates = trust_all_certificates
        self._use_path_style_addressing = use_path_style_addressing
        self._sqs_url = sqs_url
        self._metadata_tags = metadata_tags

    def build(self):
        """
        :returns: Object tree for ``OpenFabricS3DataStorage``
        :rtype: cterasdk.common.object.Object
        """
        data = Object()
        data._classname = 'OpenFabricS3DataStorage'  # pylint: disable=protected-access
        data.storage = self._storage
        data.bucket = self._bucket
        data.accessKey = self._access_key
        data.secretKey = self._secret_key
        data.endPoint = self._end_point
        data.useHttps = self._use_https
        if self._region is not None:
            data.region = self._region
        data.trustAllCertificates = self._trust_all_certificates
        data.usePathStyleAddressing = self._use_path_style_addressing
        if self._sqs_url is not None:
            data.sqsUrl = self._sqs_url
        data.metadataTags = self._metadata_tags
        return data


class OpenFabricSettingsBuilder:
    """
    Build ``OpenFabricSettings`` for :meth:`cterasdk.core.cloudfs.CloudDrives.add`
    and :meth:`cterasdk.core.cloudfs.CloudDrives.modify` (Fusion Direct).

    For S3-backed Fusion Direct folders, use a non-``Filesystem`` ``storage_mode``
    (typically :attr:`OpenFabricStorageMode.Bucket`) and an ``OpenFabricS3DataStorage``
    instance from :class:`OpenFabricS3DataStorageBuilder`.
    """

    def __init__(self, data_storage, *, storage_mode=None):
        """
        :param cterasdk.common.object.Object data_storage: Built ``OpenFabricS3DataStorage`` object
        :param str,optional storage_mode: One of :class:`OpenFabricStorageMode`; defaults to ``Bucket``
        """
        self._data_storage = data_storage
        self._storage_mode = storage_mode if storage_mode is not None else OpenFabricStorageMode.Bucket

    def build(self):
        """
        :returns: Object tree for ``OpenFabricSettings``
        :rtype: cterasdk.common.object.Object
        """
        settings = Object()
        settings._classname = 'OpenFabricSettings'  # pylint: disable=protected-access
        settings.storageMode = self._storage_mode
        settings.dataStorage = self._data_storage
        return settings
