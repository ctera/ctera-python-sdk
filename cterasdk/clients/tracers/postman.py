import aiohttp
from ...audit import postman


def tracer():

    async def on_request_start(session, ctx, params):
        # pylint: disable=unused-argument
        """
        :param aiohttp.ClientSession session: Session.
        :param cterasdk.transcriber.postman.Command ctx: Command.
        """
        ctx.stream = postman.BodyStream()
        ctx.request = postman.Request(
            params.method,
            postman.URL(
                str(params.url),
                params.url.scheme,
                params.url.host.split('.'),
                params.url.port,
                params.url.path.split('/')[1:],
                dict(params.url.query)
            )
        )

    async def on_request_headers_sent(session, ctx, params):
        # pylint: disable=unused-argument
        """
        :param aiohttp.ClientSession session: Session.
        :param cterasdk.transcriber.postman.Command ctx: Command.
        """
        ctx.request.request_headers({k: v for k, v in params.headers.items() if k in [
            'Cookie',
            'Authorization',
            'Content-Type',
            'Depth',
            'Overwrite',
            'Destination'
        ]})

    async def on_request_chunk_sent(session, ctx, params):
        # pylint: disable=unused-argument
        """
        :param aiohttp.ClientSession session: Session.
        :param cterasdk.transcriber.postman.Command ctx: Command.
        """
        ctx.stream.append(params.chunk)

    async def on_request_end(session, ctx, params):
        # pylint: disable=unused-argument
        """
        :param aiohttp.ClientSession session: Session.
        :param cterasdk.transcriber.postman.Command ctx: Command.
        """
        body = ctx.stream.deserialize(params.response.request_info.headers.get('Content-Type', None))
        if body:
            ctx.request.request_body(body)
        postman.Collection.instance().add(ctx.request)

    conf = aiohttp.TraceConfig()
    conf.on_request_start.append(on_request_start)
    conf.on_request_headers_sent.append(on_request_headers_sent)
    conf.on_request_chunk_sent.append(on_request_chunk_sent)
    conf.on_request_end.append(on_request_end)

    return conf
