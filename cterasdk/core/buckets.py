import logging

from ..common import union
from ..exceptions import CTERAException, ObjectNotFoundException
from .base_command import BaseCommand
from . import query


class Buckets(BaseCommand):
    """
    Portal Storage Node APIs
    """

    default = ['name']

    def _get_entire_object(self, name):
        try:
            return self._core.api.get(f'/locations/{name}')
        except CTERAException as error:
            raise CTERAException('Failed to get bucket', error)

    def _get_tenant_base_object_ref(self, name):
        return self._core.portals.get(name, include=['baseObjectRef']).baseObjectRef

    def get(self, name, include=None):
        """
        Get a Bucket

        :param str name: Name of the bucket
        :param list[str] include: List of fields to retrieve, defaults to ``['name']``
        """
        include = union(include or [], Buckets.default)
        include = ['/' + attr for attr in include]
        bucket = self._core.api.get_multi('/locations/' + name, include)
        if bucket.name is None:
            raise ObjectNotFoundException('Could not find bucket', f'/locations/{name}', name=name)
        return bucket

    def add(self, name, bucket, read_only=False, dedicated_to=None):
        """
        Add a Bucket

        :param str name: Name of the bucket
        :param cterasdk.core.types.Bucket bucket: Storage bucket to add
        :param bool,optional read_only: Set bucket to read-delete only, defaults to False
        :param str,optional dedicated_to: Name of a tenant, defaults to ``None``
        """
        param = bucket.to_server_object()
        param.name = name
        param.readOnly = read_only
        param.dedicated = bool(dedicated_to)
        param.dedicatedPortal = self._get_tenant_base_object_ref(dedicated_to) if dedicated_to else None

        logging.getLogger('cterasdk.core').info('Adding bucket. %s',
                                                {'name': name, 'bucket': bucket.bucket, 'type': bucket.__class__.__name__})
        response = self._core.api.add('/locations', param)
        logging.getLogger('cterasdk.core').info('Bucket added. %s',
                                                {'name': name, 'bucket': bucket.bucket, 'type': bucket.__class__.__name__})
        return response

    def modify(self, current_name, new_name=None, read_only=None, dedicated_to=None):
        """
        Modify a Bucket

        :param str current_name: The current bucket name
        :param str,optional new_name: New name
        :param bool,optional read_only: Set bucket to read-delete only
        :param bool,optional dedicated: Dedicate bucket to a tenant
        :param str,optional dedicated_to: Tenant name
        """
        param = self._get_entire_object(current_name)
        if new_name:
            param.name = new_name
        if read_only is not None:
            param.readOnly = read_only
        if dedicated_to is not None:
            if isinstance(dedicated_to, bool):
                if not dedicated_to:
                    param.dedicated = False
                    param.dedicatedPortal = None
                else:
                    raise ValueError("'dedicated_to' must be either False or a 'str'")
            elif isinstance(dedicated_to, str):
                param.dedicated = True
                param.dedicatedPortal = self._get_tenant_base_object_ref(dedicated_to) if dedicated_to else None
        logging.getLogger('cterasdk.core').info("Modifying bucket. %s", {'name': current_name})
        response = self._core.api.put(f'/locations/{current_name}', param)
        logging.getLogger('cterasdk.core').info("Bucket modified. %s", {'name': current_name})
        return response

    def list_buckets(self, include=None):
        """
        List Buckets.\n
        To retrieve buckets, you must first browse the Global Administration Portal, using: `GlobalAdmin.portals.browse_global_admin()`

        :param list[str],optional include: List of fields to retrieve, defaults to ``['name']``
        """
        include = union(include or [], Buckets.default)
        param = query.QueryParamBuilder().include(include).build()
        return query.iterator(self._core, '/locations', param)

    def delete(self, name):
        """
        Delete a Bucket

        :param str name: Name of the bucket
        """
        logging.getLogger('cterasdk.core').info('Deleting bucket. %s', {'name': name})
        response = self._core.api.delete(f'/locations/{name}')
        logging.getLogger('cterasdk.core').info('Bucket deleted. %s', {'name': name})
        return response

    def read_write(self, name):
        """
        Set bucket to Read Write

        :param str name: Name of the bucket
        """
        logging.getLogger('cterasdk.core').info('Setting bucket to read-write. %s', {'name': name})
        return self._read_only(name, False)

    def read_only(self, name):
        """
        Set bucket to Read Only

        :param str name: Name of the bucket
        """
        logging.getLogger('cterasdk.core').info('Setting bucket to read-delete only. %s', {'name': name})
        return self._read_only(name, True)

    def _read_only(self, name, enabled):
        return self._core.api.put(f'/locations/{name}/readOnly', enabled)
