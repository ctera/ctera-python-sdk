=============
CTERA SDK CLI
=============

The CTERA Python SDK includes a set of built-in executable commands that are
installed automatically as part of the SDK package. These commands provide
direct access to common SDK functionality through a command-line interface.

The following page describes the supported CLI commands and their usage.

CTERA Direct/IO Download
------------------------

The ``cterasdk.io.direct.download`` command downloads a file using **CTERA Direct I/O**.

The download is performed using the file's unique numeric **File ID** and
stores the file at a specified local path. Authentication can be performed
using either an Access/Secret key pair or a Bearer token.

Arguments
^^^^^^^^^

``--endpoint`` / ``-e``
    CTERA Portal address (for example: ``corp.acme.ctera.com``).

``--path`` / ``-p``
    Local destination path where the downloaded file will be saved
    (for example: ``./download.zip``).

``--file-id`` / ``-f``
    Numeric identifier of the file to download.

``--access`` / ``-a``
    Access key used for authentication (optional).

``--secret`` / ``-s``
    Secret key used together with the access key (optional).

``--bearer`` / ``-b``
    Bearer authentication token (optional).

``--no-verify-ssl`` / ``-k``
    Disable SSL certificate verification. Intended for testing or
    environments using self-signed certificates.

``--debug`` / ``-d``
    Enable verbose debug logging output.

Examples
^^^^^^^^

Download a file using access and secret keys:

**Bash (Linux / macOS)**

.. code-block:: bash

    cterasdk.io.direct.download \
        --endpoint corp.acme.ctera.com \
        --file-id 847362915 \
        --path "./Statement.pdf" \
        --access AKIA7F3K9X2QPLM8D4ZT \
        --secret wJalrXUtnFEMI/K7MDENG/bPxRfiCY8zEXAMPLEKEY

**Windows Command Prompt (cmd.exe)**

.. code-block:: bash

    cterasdk.io.direct.download ^
        --endpoint corp.acme.ctera.com ^
        --file-id 847362915 ^
        --path ".\Statement.pdf" ^
        --access AKIA7F3K9X2QPLM8D4ZT ^
        --secret wJalrXUtnFEMI/K7MDENG/bPxRfiCY8zEXAMPLEKEY


CTERA Portal Invitation Browser
-------------------------------

CLI to interact with external shares on CTERA Portal.

.. code-block:: bash

   cterasdk.io.dav {ls,download,upload} [options]

Commands
--------

Listing files and folders
^^^^^^^^^^^^^^^^^^^^^^^^^

``cterasdk.io.dav ls -e ENDPOINT [-s SRC] [-R]``

Downloading files and folders
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``cterasdk.io.dav download -e ENDPOINT [-s SRC] [-R] [-d DEST] [-z]``

Uploading files
^^^^^^^^^^^^^^^

``cterasdk.io.dav upload -e ENDPOINT [-d DEST] files [files ...]``
