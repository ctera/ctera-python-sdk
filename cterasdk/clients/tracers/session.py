import aiohttp
from ...exceptions import SessionExpired


def trace_config():

    async def on_request_redirect(session, context, params):
        # pylint: disable=unused-argument
        if params.response.status == 302:
            location = dict(params.response.headers).get('Location', None)
            if location in ['/ServicesPortal/login.html'] or location.startswith(('https://login.microsoftonline.com')):
                raise SessionExpired()

    tracer = aiohttp.TraceConfig()
    tracer.on_request_redirect.append(on_request_redirect)
    return tracer
