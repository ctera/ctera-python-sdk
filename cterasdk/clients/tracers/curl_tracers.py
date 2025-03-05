import logging
import aiohttp
import urllib.parse
from ...convert import fromjsonstr, tojsonstr, fromxmlstr, toxmlstr  # noqa: E402, F401


def curl_trace_config():
    """Create a trace config that outputs cURL commands for HTTP requests."""

    async def on_request_start(session, context, params):
        logger = logging.getLogger('cterasdk.http.curl')
        
        # Store request info in context for later use
        context.curl_command = ['curl']
        
        # Add method if not GET
        if params.method != 'GET':
            context.curl_command.extend(['-X', params.method])
        
        # Add URL
        context.curl_command.append(str(params.url))
        
        # Log request details for debugging
        logger.debug('Request: %s %s', params.method, params.url)
        if hasattr(params, 'headers'):
            logger.debug('Headers: %s', dict(params.headers))
        
        # Add headers
        if params.headers:
            for header_dict in [dict(params.headers)]:
                for header, value in header_dict.items():
                    context.curl_command.extend(['-H', f'{header}: {value}'])
                    logger.debug('Added header: %s: %s', header, value)

        # Handle request data
        request_data = None
        if hasattr(params, 'data') and params.data:
            request_data = params.data
            logger.debug('Found data in params.data: %s', type(request_data))
        elif hasattr(params, 'kwargs') and 'data' in params.kwargs:
            request_data = params.kwargs['data']
            logger.debug('Found data in params.kwargs[data]: %s', type(request_data))

        if request_data:
            try:
                # Try to decode as UTF-8 if bytes
                if isinstance(request_data, bytes):
                    request_data = request_data.decode('utf-8')
                    logger.debug('Decoded bytes to string: %s', request_data[:100])

                # Handle different data types
                if isinstance(request_data, str):
                    # Check if it's XML
                    if request_data.startswith('<?xml') or request_data.startswith('<obj') or request_data.startswith('<val'):
                        logger.debug('Detected XML data: %s', request_data[:100])
                        context.curl_command.extend(['-H', 'Content-Type: application/xml'])
                        context.curl_command.extend(['-d', request_data])
                    # Check if it's URL-encoded form data
                    elif '=' in request_data and not request_data.startswith('{'):
                        logger.debug('Detected form data: %s', request_data)
                        context.curl_command.extend(['-H', 'Content-Type: application/x-www-form-urlencoded'])
                        # Parse form data
                        form_data = urllib.parse.parse_qs(request_data)
                        for key, values in form_data.items():
                            for value in values:
                                context.curl_command.extend(['-d', f'{key}={value}'])
                    else:
                        # Try parsing as JSON
                        try:
                            json_data = fromjsonstr(request_data)
                            logger.debug('Detected JSON data: %s', tojsonstr(json_data)[:100])
                            context.curl_command.extend(['-H', 'Content-Type: application/json'])
                            context.curl_command.extend(['-d', tojsonstr(json_data)])
                        except Exception:
                            # Raw data
                            logger.debug('Using raw data: %s', request_data[:100])
                            context.curl_command.extend(['-d', request_data])
                elif isinstance(request_data, dict):
                    # Handle dictionary data
                    logger.debug('Detected dictionary data: %s', request_data)
                    context.curl_command.extend(['-H', 'Content-Type: application/json'])
                    context.curl_command.extend(['-d', tojsonstr(request_data)])
                elif isinstance(request_data, aiohttp.FormData):
                    # Handle form data
                    logger.debug('Detected FormData object')
                    context.curl_command.extend(['-H', 'Content-Type: application/x-www-form-urlencoded'])
                    for field in request_data._fields:
                        name = field[0]
                        value = field[2]
                        if isinstance(value, bytes):
                            value = value.decode('utf-8')
                        context.curl_command.extend(['-d', f'{name}={value}'])
            except Exception as e:
                logger.debug('Error processing request data: %s', e)
                # Fall back to sending raw data
                context.curl_command.extend(['-d', str(request_data)])

    async def on_request_chunk_sent(session, context, params):
        if not hasattr(params, 'chunk') or not params.chunk:
            return
            
        try:
            # Try to decode as UTF-8
            chunk_str = params.chunk.decode('utf-8') if isinstance(params.chunk, bytes) else str(params.chunk)
            
            # If it looks like form data
            if '=' in chunk_str and not chunk_str.startswith('<'):  # Not XML
                try:
                    # Parse form data
                    form_params = urllib.parse.parse_qs(chunk_str)
                    context.curl_command.extend(['-H', 'Content-Type: application/x-www-form-urlencoded'])
                    for key, values in form_params.items():
                        for value in values:
                            context.curl_command.extend(['-d', f'{key}={value}'])
                except Exception:
                    context.curl_command.extend(['-d', chunk_str])
            else:
                # Check if it's XML
                if chunk_str.startswith('<?xml') or chunk_str.startswith('<obj') or chunk_str.startswith('<val'):
                    context.curl_command.extend(['-H', 'Content-Type: application/xml'])
                    context.curl_command.extend(['-d', chunk_str])
                else:
                    # Try parsing as JSON
                    try:
                        json_data = fromjsonstr(chunk_str)
                        context.curl_command.extend(['-H', 'Content-Type: application/json'])
                        context.curl_command.extend(['-d', tojsonstr(json_data)])
                    except Exception:
                        # Raw data
                        if chunk_str.strip():  # Only add if not empty
                            context.curl_command.extend(['-d', chunk_str])
        except UnicodeDecodeError:
            context.curl_command.extend(['-d', '@binary_data'])

    async def on_request_end(session, context, params):
        if hasattr(context, 'curl_command'):
            # Format the command with proper escaping and indentation
            formatted_parts = []
            for i, part in enumerate(context.curl_command):
                # Escape single quotes and wrap in single quotes
                escaped_part = part.replace("'", "'\\''")
                if i == 0:  # First part (curl)
                    formatted_parts.append(f"'{escaped_part}'")
                elif part in ['-X', '-H', '-d']:  # New option
                    formatted_parts.append(f"\\\n    '{escaped_part}'")
                else:  # Option value
                    formatted_parts.append(f" '{escaped_part}'")
            
            # Always log the command, even if it's just curl and URL
            logging.getLogger('cterasdk.http.curl').info('\n%s', ''.join(formatted_parts))

    trace_config = aiohttp.TraceConfig()
    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_chunk_sent.append(on_request_chunk_sent)
    trace_config.on_request_end.append(on_request_end)
    
    return trace_config 