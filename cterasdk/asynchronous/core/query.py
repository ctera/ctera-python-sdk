from .iterator import QueryAsyncIterator
from ...core.query import QueryParams
from ...lib import DefaultResponse, Command


def create_callback_function(core, path, name=None, *, callback_response=None):
    """
    Create a query callback function

    :param cterasdk.objects.core.Portal core: Portal object
    :param cterasdk.core.query.QueryParams param: Query paramter object
    :param str,optional name: Schema method name
    :param cterasdk.lib.iterator.BaseResponse callback_response: Class to consume callback response

    :returns: Command object
    """

    async def database(core, path, name, param):
        return callback_response(await core.v1.api.database(path, name, param))

    return Command(database, core, path, name or 'query')


def iterator(core, path, param=None, name=None, *, callback_response=None):
    """
    Create iterator

    :param cterasdk.objects.core.Portal core: Portal object
    :param str path: URL Path
    :param str,optional name: Schema method name
    :param cterasdk.core.query.QueryParams,optional param: Query paramter object
    :param cterasdk.lib.iterator.BaseResponse callback_response: Class to consume callback response

    :returns: Query iterator object
    """

    callback_response = callback_response if callback_response else DefaultResponse
    callback_function = create_callback_function(core, path, name, callback_response=callback_response)
    return QueryAsyncIterator(callback_function, param if param else QueryParams())
