import json
import logging
import aiohttp


logger = logging.getLogger('cterasdk.http')


def tracer():

    async def on_request_start(session, context, params):
        # pylint: disable=unused-argument
        param = {
            'request': {
                'method': params.method,
                'url': str(params.url),
                'headers': [dict(params.headers)] if params.headers else []
            }
        }
        logger.debug('Starting request. %s', serialize(param))

    async def on_request_redirect(session, context, params):
        # pylint: disable=unused-argument
        param = {
            'redirect': {
                'source': str(params.response.real_url),
                'destination': params.response.headers['Location']
            }
        }
        logger.debug('Starting redirect. %s', serialize(param))

    async def on_request_end(session, context, params):
        # pylint: disable=unused-argument
        param = {
            'request': {
                'method': params.response.method,
                'url': str(params.response.real_url),
                'headers': [dict(params.response.request_info.headers)]
            },
            'response': {
                'status': params.response.status,
                'reason': params.response.reason,
                'headers': [dict(params.response.headers)]
            }
        }
        logger.debug('Ended request. %s', serialize(param))

    conf = aiohttp.TraceConfig()
    conf.on_request_start.append(on_request_start)
    conf.on_request_redirect.append(on_request_redirect)
    conf.on_request_end.append(on_request_end)

    return conf


def serialize(param):
    return json.dumps(param, indent=5)
