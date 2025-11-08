import sys
import asyncio
import logging
import argparse
import aiofiles
import yarl


from .. import settings
from ..common import utils
from ..lib.storage import commonfs
from .client import DirectIO
from ..exceptions.direct import StreamError, DirectIOError
from ..exceptions.transport import TLSError


logging.basicConfig(format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", level=logging.ERROR)


logger = logging.getLogger('cterasdk.direct')


def validate_endpoint(endpoint):
    baseurl, port = yarl.URL(endpoint), 443
    logger.debug('Validating connection to host: %s on port: %s', baseurl.host, port)
    utils.tcp_connect(baseurl.host, port, timeout=5)
    return f'{baseurl}'


def validate_directory_and_filename(path):
    directory, filename = commonfs.generate_file_destination(path)
    assert all([directory, filename]), f'Error: Could not resolve file path: {path}'


async def download_from_object_storage(options, file_id, path):
    async with DirectIO(**options) as client:
        streamer = await client.streamer(file_id)
        try:
            async with aiofiles.open(path, 'wb') as fd:
                async for block in streamer.start():
                    await fd.seek(block.offset)
                    await fd.write(block.data)
        except StreamError as e:
            print(f'Download failed. Cause: {e.__cause__}', file=sys.stderr)


def download_object():
    parser = argparse.ArgumentParser(
        description="Download a file from CTERA Portal via CTERA Direct I/O."
    )

    arguments = [
        ("--endpoint", "-e", {"type": str, "required": True, "help": "CTERA Portal (e.g. corp.acme.ctera.com)"}),
        ("--path", "-p", {"type": str, "required": True, "help": "File path (e.g. ./download.zip)"}),
        ("--access", "-a", {"type": str, "help": "Access Key (optional)"}),
        ("--secret", "-s", {"type": str, "help": "Secret Key (optional)"}),
        ("--bearer", "-b", {"type": str, "help": "Bearer token (optional)"}),
        ("--file-id", "-f", {"required": True, "type": int, "help": "File ID (numeric)"}),
        ("--no-verify-ssl", "-k", {"action": "store_true", "help": "Disable SSL verification"}),
        ("--debug", "-d", {"action": "store_true", "help": "Enable debug logging"}),
    ]

    for lopt, sopt, options in arguments:
        parser.add_argument(lopt, sopt, **options)

    args = parser.parse_args()

    try:

        if args.debug:
            logger.setLevel(logging.DEBUG)

        options = {
            'baseurl': validate_endpoint(args.endpoint),
            'access_key_id': args.access,
            'secret_access_key': args.secret,
            'bearer': args.bearer
        }

        validate_directory_and_filename(args.path)

        settings.io.direct.api.settings.connector.ssl = not args.no_verify_ssl
        settings.io.direct.storage.settings.connector.ssl = not args.no_verify_ssl

        asyncio.run(download_from_object_storage(options, args.file_id, args.path))
    except ConnectionError:
        print(f'Error: Could not establish connection to host: {args.endpoint}:443', file=sys.stderr)
    except (AssertionError, TLSError, DirectIOError) as e:
        print(e, file=sys.stderr)
