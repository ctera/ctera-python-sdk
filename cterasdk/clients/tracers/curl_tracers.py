import json
import logging
import aiohttp
import shlex
import urllib.parse


def curl_trace_config():
    """Create a trace config that outputs cURL commands for HTTP requests."""

    async def on_request_start(session, context, params):
        # Store request info in context for later use
        context.curl_command = ['curl']
        
        # Debug log to see what we're getting
        debug_logger = logging.getLogger('cterasdk.http.debug')
        debug_logger.debug("Request params: %s", {
            'method': params.method,
            'url': str(params.url),
            'headers': dict(params.headers) if params.headers else {},
            'data': getattr(params, 'data', None),
            'kwargs': getattr(params, 'kwargs', {}),
            'request_info': getattr(params, 'request_info', None)
        })
        
        # Add method if not GET
        if params.method != 'GET':
            context.curl_command.extend(['-X', params.method])
        
        # Add URL
        context.curl_command.append(str(params.url))
        
        # Add headers
        if params.headers:
            for header_dict in [dict(params.headers)]:
                for header, value in header_dict.items():
                    context.curl_command.extend(['-H', f'{header}: {value}'])

    async def on_request_chunk_sent(session, context, params):
        # pylint: disable=unused-argument
        debug_logger = logging.getLogger('cterasdk.http.debug')
        debug_logger.debug("Chunk sent: %s", params)
        
        if hasattr(params, 'chunk'):
            try:
                # Try to decode as UTF-8
                chunk_str = params.chunk.decode('utf-8') if isinstance(params.chunk, bytes) else str(params.chunk)
                debug_logger.debug("Chunk data: %s", chunk_str)
                
                # If it looks like form data
                if '=' in chunk_str:
                    try:
                        # Parse form data
                        form_params = urllib.parse.parse_qs(chunk_str)
                        context.curl_command.extend(['-H', 'Content-Type: application/x-www-form-urlencoded'])
                        for key, values in form_params.items():
                            for value in values:
                                context.curl_command.extend(['-d', f'{key}={value}'])
                    except Exception as e:
                        debug_logger.warning("Failed to parse form data: %s", str(e))
                        context.curl_command.extend(['-d', chunk_str])
                else:
                    # Try parsing as JSON
                    try:
                        json_data = json.loads(chunk_str)
                        context.curl_command.extend(['-H', 'Content-Type: application/json'])
                        context.curl_command.extend(['-d', json.dumps(json_data)])
                    except json.JSONDecodeError:
                        # Raw data
                        context.curl_command.extend(['-d', chunk_str])
            except UnicodeDecodeError:
                debug_logger.warning("Failed to decode chunk as UTF-8")
                context.curl_command.extend(['-d', '@binary_data'])

    async def on_request_end(session, context, params):
        # pylint: disable=unused-argument
        if hasattr(context, 'curl_command'):
            # Format the command with proper escaping
            formatted_command = ' \\\n     '.join(shlex.quote(part) for part in context.curl_command)
            logging.getLogger('cterasdk.http.curl').info('\n%s', formatted_command)

    trace_config = aiohttp.TraceConfig()
    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_chunk_sent.append(on_request_chunk_sent)
    trace_config.on_request_end.append(on_request_end)
    
    return trace_config 