import os
import sys
import asyncio
import argparse
from pathlib import Path
from ..core.enum import FileAccessMode
from ..lib.storage import asynfs, commonfs
from ..objects.asynchronous.invitation import AsyncInvitation
from ..exceptions.io.core import ListDirectoryError, GetMetadataError


async def handle_ls(args):

    attributes = [
        ("ID", 12),
        ("VOLUME", 7),
        ("SIZE", 10),
        ("MODIFIED", 15),
        ("DELETED", 8),
        ("DIR", 4),
        ("PATH", 50)
    ]

    async with AsyncInvitation.from_uri(args.endpoint) as invitation:
        func = invitation.files.walk if args.recursive else invitation.files.listdir

        rows = [
            (
                o.id,
                o.volume.id,
                o.size,
                o.last_modified.strftime("%b %#d, %H:%M"),
                'true' if o.deleted else 'false',
                'd' if o.is_dir else 'f',
                o.path.relative,
            )
            async for o in func()
        ]

        if rows:
            formatter = " ".join(f"{{:<{width}}}" for _, width in attributes)
            print(formatter.format(*(name for name, _ in attributes)))
            for row in rows:
                print(formatter.format(*row))


async def handle_download(args):  # pylint: disable=too-many-branches
    target = Path(args.dest or os.getcwd())

    try:

        Path.mkdir(target, exist_ok=True)

        async def download(invitation, resource, objects=None, archive=False, destination=None):
            if objects is not None or archive:
                return await invitation.files.download_many(resource.path.relative, [o.name for o in objects], f'{destination}.zip')
            return await invitation.files.download(resource.path.relative, destination.joinpath(resource.path.relative))

        async with AsyncInvitation.from_uri(args.endpoint) as invitation:
            jobs = []

            if not invitation.details.is_dir:  # pylint: disable=too-many-nested-blocks
                if args.src:
                    print(f"error: object not found error: '{args.src}'", file=sys.stderr)
                    sys.exit(1)
                resource = await invitation.files.listdir().__anext__()
                jobs.append(download(invitation, resource, destination=target))
            else:
                try:
                    resource = await invitation.files.properties(args.src)
                    if not resource.is_dir:
                        jobs.append(download(invitation, resource, destination=target))
                    else:
                        enumerator = invitation.files.walk if args.recursive else invitation.files.listdir
                        objects = [r async for r in enumerator(args.src)]
                        if args.archive:
                            jobs.append(download(invitation, resource, objects, True, target.joinpath(args.src or invitation.invite)))
                        else:
                            for r in objects:
                                if r.is_dir:
                                    await asynfs.mkdir(target.joinpath(r.path.relative), parents=True, exist_ok=True)
                                else:
                                    jobs.append(download(invitation, r, destination=target))
                except (GetMetadataError, ListDirectoryError):
                    print(f"error: failed to obtain properties or list a directory: '{args.src}'", file=sys.stderr)
                    sys.exit(1)

            await asyncio.gather(*jobs)

    except PermissionError:
        print(f"error: permission denied: Cannot create files and folders at '{target}'.", file=sys.stderr)
    except NotADirectoryError:
        print(f"error: path conflict: '{target}' is a file, but a folder was expected.", file=sys.stderr)
    except OSError as e:
        print(f"error: an unexpected error occurred during download. {e}", file=sys.stderr)


async def handle_upload(args):

    for p in args.files:
        if not commonfs.exists(p):
            print(f"error: path not found: '{p}'", file=sys.stderr)
            sys.exit(1)

    async with AsyncInvitation.from_uri(args.endpoint) as invitation:
        if not invitation.details.is_dir:
            print("error: destination is not a directory", file=sys.stderr)
            sys.exit(1)
        elif invitation.details.access not in [FileAccessMode.RW, FileAccessMode.UO]:
            print(f"error: insufficient permissions to write to: {args.dest}", file=sys.stderr)
            sys.exit(1)

        try:
            destination = args.dest or '.'
            if args.dest:
                properties = await invitation.files.properties(args.dest)
                if not properties.is_dir:
                    print(f"error: destination is not a directory: '{args.dest}'", file=sys.stderr)
                    sys.exit(1)
                destination = properties.path.relative

            jobs = []
            for p in args.files:
                jobs.append(invitation.files.upload_file(p, destination))

            await asyncio.gather(*jobs)

        except GetMetadataError:
            print(f"error: failed to obtain properties for directory: '{args.dest}'", file=sys.stderr)
            sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(prog="cterasdk.io.dav")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ls = subparsers.add_parser("ls", help="list directory contents")
    ls.add_argument("-e", "--endpoint", type=str, required=True, help="CTERA Portal endpoint, or external share")
    ls.add_argument("-s", "--src", type=str, required=False, help="path to file or folder")
    ls.add_argument("-R", "--recursive", action="store_true", help="list subdirectories recursively")
    ls.set_defaults(func=handle_ls)

    download = subparsers.add_parser("download", help="download files or folders")
    download.add_argument("-e", "--endpoint", type=str, required=True, help="CTERA Portal endpoint, or external share")
    download.add_argument("-s", "--src", type=str, required=False, help="path to file or folder")
    download.add_argument("-R", "--recursive", action="store_true", help="download sub-directories and files")
    download.add_argument("-d", "--dest", type=str, help="destination path on local file system")
    download.add_argument("-z", "--archive", action="store_true", help="download as zip archive (applicable to directories)")
    download.set_defaults(func=handle_download)

    upload = subparsers.add_parser("upload", help="upload files")
    upload.add_argument("files", type=str, nargs='+', help="one or more local files")
    upload.add_argument("-e", "--endpoint", type=str, required=True, help="CTERA Portal endpoint, or external share")
    upload.add_argument("-d", "--dest", type=str, required=False, help="destination folder")
    upload.set_defaults(func=handle_upload)

    args = parser.parse_args()
    await args.func(args)


def webdav():
    asyncio.run(main())
