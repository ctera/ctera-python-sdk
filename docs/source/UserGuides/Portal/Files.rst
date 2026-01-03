===============
File Browser
===============

This article describes the file-browser APIs available in the CTERA Portal, which provide programmatic access to files and directories.

The APIs support both **synchronous** and **asynchronous** execution models, enabling developers to choose the approach best suited to their integration needs, from real-time operations to background processing.

Preface: Authentication
=======================

All file-browser operations require an authenticated session with the CTERA Portal.
Authentication is performed by creating a portal context and calling ``login`` with valid credentials.

Once authenticated, the ``files`` attribute provides access to the file-browser APIs.

Synchronous Authentication
--------------------------

Set ``cterasdk.settings.core.syn.settings.connector.ssl = False`` to disable SSL verification.

Authenticate as a tenant user using ``ServicesPortal``:

.. code-block:: python

   with ServicesPortal('tenant.ctera.com') as user:
       user.login(username, password)
       files = user.files

Authenticate as a global administrator using ``GlobalAdmin``:

.. code-block:: python

   with GlobalAdmin('global.ctera.com') as admin:
       admin.login(username, password)
       files = admin.files

Asynchronous Authentication
---------------------------

Set ``cterasdk.settings.core.asyn.settings.connector.ssl = False`` to disable SSL verification.

Authenticate as a tenant user using ``AsyncServicesPortal``:

.. code-block:: python

   async with AsyncServicesPortal('tenant.ctera.com') as user:
       await user.login(username, password)
       files = user.files

Authenticate as a global administrator using ``AsyncGlobalAdmin``:

.. code-block:: python

   async with AsyncGlobalAdmin('global.ctera.com') as admin:
       await admin.login(username, password)
       files = admin.files

User Roles and Permissions
==========================

The file access APIs are available to the following user roles:

- **Global Administrators** with the ``Access End User Folders`` permission enabled.
- **Team Portal Administrators** with the ``Access End User Folders`` permission enabled.
- **End Users**, accessing their personal cloud drive folders.

For more information about configuring administrator permissions, see
`Customizing Administrator Roles <https://kb.ctera.com/docs/customizing-administrator-roles-2>`_.

Key Objects
===========

This section describes the core objects returned by the file-browser APIs.

.. autoclass:: cterasdk.cio.core.types.PortalResource
   :members:
   :undoc-members:

.. autoclass:: cterasdk.cio.core.types.PortalVolume
   :members:
   :undoc-members:

.. autoclass:: cterasdk.cio.core.types.VolumeOwner
   :members:
   :undoc-members:

.. autoclass:: cterasdk.cio.core.types.PreviousVersion
   :members:
   :undoc-members:

Synchronous API
===============

Listing Files and Directories
-----------------------------

.. automethod:: cterasdk.core.files.browser.FileBrowser.listdir
   :noindex:

.. code-block:: python

   resources = files.listdir('My Files')
   for r in resources:
       print(r.name, r.is_dir)

.. automethod:: cterasdk.core.files.browser.FileBrowser.walk
   :noindex:

.. code-block:: python

   for resource in files.walk('My Files'):
       if not resource.is_dir and resource.extension == 'pdf':
           files.download(resource.path)

Listing Files from Previous Versions
-----------------------------------

.. automethod:: cterasdk.core.files.browser.FileBrowser.versions
   :noindex:

.. code-block:: python

   # List all versions of a file
   versions = files.versions('My Files/Keystone Project.docx')
   for v in versions:
       print(v.start_time, v.end_time, v.current)

   # List files in a previous version
   prev_version = next(v for v in versions if not v.current)
   for f in files.listdir(prev_version.path):
       print(f'File in previous version: {f.path}, Size: {f.size}, Last modified: {f.last_modified}')

   # Download files from a previous version
   for f in files.listdir(prev_version.path):
       local_path = files.download(f.path)
       print(local_path)

Inspecting Files
----------------

.. automethod:: cterasdk.core.files.browser.FileBrowser.properties
   :noindex:

.. code-block:: python

   metadata = files.properties('My Files/Keystone Project.docx')
   print(metadata.size, metadata.last_modified)

.. automethod:: cterasdk.core.files.browser.FileBrowser.exists
   :noindex:

.. code-block:: python

   exists = files.exists('My Files/Keystone Project.docx')

Retrieve a Permalink
--------------------

.. automethod:: cterasdk.core.files.browser.FileBrowser.permalink
   :noindex:

.. code-block:: python

   permalink = files.permalink('My Files/Keystone Project.docx')
   print(f'Permalink: {permalink}')

Create a Public Link
--------------------

.. automethod:: cterasdk.core.files.browser.FileBrowser.public_link
   :noindex:

.. code-block:: python

   public_url = files.public_link('My Files/Keystone Project.docx', access='RO', expire_in=7)
   print(f'Public link: {public_url}')

   preview_link = files.public_link('My Files/Keystone Market Overview.pdf', access='PO', expire_in=7)
   print(f'Preview-only link: {preview_link}')

   public_url_rw = files.public_link('My Files', access='RW', expire_in=30)
   print(f'Public read-write link: {public_url_rw}')

File Handles
------------

.. automethod:: cterasdk.core.files.browser.FileBrowser.handle
   :noindex:

.. code-block:: python

   handle = files.handle('My Files/Keystone Project.docx')

.. automethod:: cterasdk.core.files.browser.FileBrowser.handle_many

.. code-block:: python

   handle = files.handle_many('My Files', 'Keystone Project.docx', 'Images', 'Notes.txt')

Downloading Files
-----------------

.. automethod:: cterasdk.core.files.browser.FileBrowser.download
   :noindex:

.. code-block:: python

   local_path = files.download('My Files/Keystone Project.docx')

.. automethod:: cterasdk.core.files.browser.FileBrowser.download_many
   :noindex:

.. code-block:: python

   zip_path = files.download_many('My Files', ['Keystone Project.docx', 'Images'], destination='/tmp/MyFiles.zip')

Create Directories
------------------

.. automethod:: cterasdk.core.files.cloud.CloudDrive.mkdir
   :noindex:

.. code-block:: python

   new_dir = files.mkdir('My Files/NewProject')
   print(f'Created directory: {new_dir}')

.. automethod:: cterasdk.core.files.cloud.CloudDrive.makedirs
   :noindex:

.. code-block:: python

   nested_dir = files.makedirs('My Files/Projects/2026/Q1')
   print(f'Created nested directories: {nested_dir}')

Uploading Files
---------------

.. automethod:: cterasdk.core.files.cloud.CloudDrive.upload_file
   :noindex:

.. code-block:: python

   # Upload from a local path to a directory
   remote_path = files.upload_file('/tmp/Keystone Project.docx', 'My Files')
   print(f'File uploaded to: {remote_path}')

   # Upload from a local path and rename the file at the destination
   remote_path = files.upload_file('/tmp/Keystone Project.docx', 'My Files/Keystone 2026.docx')
   print(f'File uploaded to: {remote_path}')

.. automethod:: cterasdk.core.files.cloud.CloudDrive.upload
   :noindex:

.. code-block:: python

   name = 'Keystone Project.docx'
   destination = 'My Files'
   
   # Upload from file handle
   with open('/tmp/Keystone Project.docx', 'rb') as f:
       remote_path = files.upload(name, destination, f)
   print(f'File uploaded from handle to: {remote_path}')

   # Upload from string or bytes
   remote_path = files.upload(name, destination, handle=b'Sample content for ProjectPlan.')
   print(f'File uploaded from bytes to: {remote_path}')

Renaming Files and Folders
--------------------------

.. automethod:: cterasdk.core.files.cloud.CloudDrive.rename
   :noindex:

.. code-block:: python

   remote_path = files.rename('My Files/Keystone Project.docx', 'Keystone Project 2026.docx')
   print(f'Renamed file: {remote_path}')

Copying and Moving Files and Folders
------------------------------------

.. automethod:: cterasdk.core.files.browser.FileBrowser.copy
   :noindex:

.. code-block:: python

   # Copy files into a destination directory
   result = files.copy('My Files/Keystone Project.docx', 'My Files/Keystone Notes.txt', destination='Archive')
   print(f'Files copied: {result}')

   # Copy multiple files at once while renaming them. Requires explicitly defining the target path
   result = files.copy(
       ('My Files/Keystone Project.docx', 'Archive/Keystone Project 2026.docx'),
       ('My Files/Keystone Notes.txt', 'Archive/Keystone Notes 2026.txt')
   )
   print(f'Files copied with explicit paths: {result}')

.. automethod:: cterasdk.core.files.browser.FileBrowser.move
   :noindex:

.. code-block:: python

   # Move files into a destination directory
   result = files.move('My Files/Keystone Project.docx', 'My Files/Keystone Notes.txt', destination='Archive')
   print(f'Files moved: {result}')

   # Move multiple files at once while renaming them. Requires explicitly defining the target path
   result = files.move(
       ('My Files/Keystone Project.docx', 'Archive/Keystone 2026.docx'),
       ('My Files/Keystone Notes.txt', 'Archive/Keystone Notes 2026.txt')
   )
   print(f'Files moved with explicit paths: {result}')

Delete or Recovering Files and Folders
--------------------------------------

.. automethod:: cterasdk.core.files.cloud.CloudDrive.delete
   :noindex:

.. code-block:: python

   result = files.delete('My Files/Project Keystone.docx')
   print(f'Deleted file: {result}')

   result = files.delete('My Files/Project Keystone.docx', 'My Files/Keystone Notes.txt', 'Archive/Keystone')
   print(f'Deleted multiple files/folders: {result}')

.. automethod:: cterasdk.core.files.cloud.CloudDrive.undelete
   :noindex:

.. code-block:: python

   result = files.undelete('My Files/Project Keystone.docx')
   print(f'Recovered file: {result}')

   result = files.undelete('My Files/Project Keystone.docx', 'My Files/Keystone Notes.txt', 'Archive/Keystone')
   print(f'Recovered multiple files/folders: {result}')

Collaboration Shares
--------------------

This section describes the main objects used for managing collaboration shares.

.. autoclass:: cterasdk.core.types.UserAccount
   :members:
   :undoc-members:


.. autoclass:: cterasdk.core.types.GroupAccount
   :members:
   :undoc-members:


.. autoclass:: cterasdk.core.types.Collaborator
   :members:
   :undoc-members:

.. automethod:: cterasdk.core.files.browser.CloudDrive.share
   :noindex:

.. code-block:: python

   alice = core_types.UserAccount('alice')
   engineers = core_types.GroupAccount('Engineers')

   alice_rcpt = core_types.Collaborator.local_user(alice).expire_in(30).read_only()
   engineers_rcpt = core_types.Collaborator.local_group(engineers).read_write()

   user.files.share('Codebase', [alice_rcpt, engineers_rcpt])

.. code-block:: python

   jsmith = core_types.Collaborator.external('jsmith@hotmail.com').expire_in(10).preview_only()
   user.files.share('My Files/Projects/2020/ProjectX', [jsmith])

   jsmith = core_types.Collaborator.external('jsmith@hotmail.com', True).expire_in(5).read_only()
   user.files.share('My Files/Projects/2020/ProjectX', [jsmith])

.. code-block:: python

   albany_group = core_types.GroupAccount('Albany', 'ctera.com')
   cleveland_group = core_types.GroupAccount('Cleveland', 'ctera.com')

   albany_rcpt = core_types.Collaborator.domain_group(albany_group).read_write()
   cleveland_rcpt = core_types.Collaborator.domain_group(cleveland_group).read_only()

   user.files.share('Cloud/Albany', [albany_rcpt, cleveland_rcpt])

.. automethod:: cterasdk.core.files.browser.CloudDrive.add_share_recipients
   :noindex:

.. code-block:: python

   engineering = core_types.GroupAccount('Engineering')
   engineering_rcpt = core_types.Collaborator.local_group(engineering).read_write()
   user.files.add_share_recipients('My Files/Projects/2020/ProjectX', [engineering_rcpt])

.. automethod:: cterasdk.core.files.browser.CloudDrive.remove_share_recipients
   :noindex:

.. code-block:: python

   alice = core_types.UserAccount('alice')
   engineering = core_types.GroupAccount('Engineering')
   user.files.remove_share_recipients('My Files/Projects/2020/ProjectX', [alice, engineering])

.. automethod:: cterasdk.core.files.browser.CloudDrive.unshare
   :noindex:

.. code-block:: python

   user.files.unshare('Codebase')
   user.files.unshare('My Files/Projects/2020/ProjectX')
   user.files.unshare('Cloud/Albany')

Managing S3 Credentials
-----------------------

CTERA Portal supports programmatic access to cloud storage via the S3 protocol, also known as *CTERA Fusion*.
This allows users and administrators to manage files and folders using standard S3 tools and SDKs, such as the Amazon SDK for Python (`boto3 <https://pypi.org/project/boto3/>`_).

For details on enabling CTERA Fusion and supported S3 features, 
see the `CTERA KB article <https://kb.ctera.com/docs/setting-up-access-to-portal-content-using-the-s3-api-ctera-fusion>`_.

The following example demonstrates how to create S3 credentials and interact with the portal using `boto3`.

.. code-block:: python

   import boto3

   bucket = 'my-bucket-name'
   local_file = './ProjectOverview.docx'
   remote_key = 'documents/ProjectOverview.docx'
   download_file = './ProjectOverview_Copy.docx'

   # CTERA Fusion: Create S3 credentials (user or admin)
   creds = user.credentials.s3.create()  # or admin.credentials.s3.create(core_types.UserAccount('username', 'domain'))

   # Instantiate boto3 client
   client = boto3.client('s3', endpoint_url='https://tenant.ctera.com:8443', aws_access_key_id=creds.accessKey,
                         aws_secret_access_key=creds.secretKey, verify=False)

   # List buckets
   for b in client.list_buckets()['Buckets']:
       print(b['Name'])

   # Upload a file
   client.upload_file(local_file, bucket, remote_key)

   # List files in a bucket
   for item in client.list_objects_v2(Bucket=bucket).get('Contents', []):
       print(item['Key'], item['LastModified'])

   # List files with pagination
   for page in client.get_paginator('list_objects_v2').paginate(Bucket=bucket):
       for item in page.get('Contents', []):
           print(item['Key'], item['LastModified'])

   # Download a file
   client.download_file(bucket, remote_key, download_file)

.. note::

   For more details on using the Amazon SDK for Python (`boto3`), refer to the official `boto3 documentation <https://boto3.amazonaws.com/v1/documentation/api/latest/index.html>`_.

Asynchronous API
================

.. automethod:: cterasdk.asynchronous.core.files.browser.FileBrowser.handle
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.FileBrowser.handle_many
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.FileBrowser.download
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.FileBrowser.download_many
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.FileBrowser.listdir
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.FileBrowser.versions
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.FileBrowser.walk
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.FileBrowser.public_link
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.FileBrowser.copy
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.CloudDrive.move
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.FileBrowser.permalink
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.CloudDrive.upload
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.CloudDrive.upload_file
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.CloudDrive.mkdir
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.CloudDrive.makedirs
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.CloudDrive.rename
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.CloudDrive.delete
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.CloudDrive.undelete
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.CloudDrive.share
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.CloudDrive.add_share_recipients
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.CloudDrive.remove_share_recipients
   :noindex:

.. automethod:: cterasdk.asynchronous.core.files.browser.CloudDrive.unshare
   :noindex:
