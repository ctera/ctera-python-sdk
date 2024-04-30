import json
import logging
import aiohttp


def default():

    async def on_request_start(session, context, params):
        # pylint: disable=unused-argument
        param = {
            'request': {
                'method': params.method,
                'url': str(params.url),
                'headers': [dict(params.headers)] if params.headers else []
            }
        }
        logging.getLogger('cterasdk.http.trace').debug('Starting request. %s', serialize(param))

    async def on_request_redirect(session, context, params):
        # pylint: disable=unused-argument
        param = {
            'redirect': {
                'source': str(params.response.real_url),
                'destination': params.response.headers['Location']
            }
        }
        logging.getLogger('cterasdk.http.trace').debug('Starting redirect. %s', serialize(param))

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
        logging.getLogger('cterasdk.http.trace').debug('Ended request. %s', serialize(param))

    trace_config = aiohttp.TraceConfig()
    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_redirect.append(on_request_redirect)
    trace_config.on_request_end.append(on_request_end)

    return trace_config


def serialize(param):
    return json.dumps(param, indent=5)
