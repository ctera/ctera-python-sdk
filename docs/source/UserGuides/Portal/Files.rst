============
File Browser
============

List
====

.. automethod:: cterasdk.core.files.browser.FileBrowser.listdir
   :noindex:

.. code:: python

   with GlobalAdmin('tenant.ctera.com') as admin:
      admin.login('admin-user', 'admin-pass')
      admin.files.listdir('Users/John Smith/My Files')
      admin.files.listdir('Users/John Smith/My Files', include_deleted=True)  # include deleted files

   with ServicesPortal('tenant.ctera.com') as user:
      user.login('username', 'user-password')
      user.files.listdir('My Files/Documents')
      user.files.listdir('My Files/Documents', include_deleted=True)  # include deleted files

.. automethod:: cterasdk.core.files.browser.FileBrowser.walk
   :noindex:

.. code:: python

   with GlobalAdmin('tenant.ctera.com') as admin:
      admin.login('admin-user', 'admin-pass')
      for element in admin.files.walk('Users/John Smith/My Files'):
         print(element.name)  # traverse John Smith's 'My Files' directory and print the name of all files and folders

   with ServicesPortal('tenant.ctera.com') as user:
      user.login('username', 'user-password')
      for element in user.files.walk('My Files/Documents'):
         print(element.name)  # as a user, traverse all and print the name of all files and folders in 'My Files/Documents'

Snapshots
=========

.. automethod:: cterasdk.core.files.browser.FileBrowser.list_snapshots
   :noindex:

.. code:: python

   with GlobalAdmin('tenant.ctera.com') as admin:
      admin.login('admin-user', 'admin-pass')
      # List all snapshots for a path
      snapshots = admin.files.list_snapshots('Users/John Smith/My Files')
      for snapshot in snapshots:
         print(f"Snapshot from: {snapshot.startTimestamp}")
         print(f"URL: {snapshot.url}")
         # Access files in this snapshot using listdir
         files = admin.files.listdir(f"{snapshot.url}")

Download
========

.. automethod:: cterasdk.core.files.browser.FileBrowser.download
   :noindex:

.. code:: python

   """When logged in as a Global Administrator"""
   admin.files.download('Users/John Smith/My Files/Documents/Sample.docx')

   """When logged in as a tenant user or admin"""
   user.files.download('Users/John Smith/My Files/Documents/Sample.docx')

.. automethod:: cterasdk.core.files.browser.FileBrowser.download_as_zip
   :noindex:

.. code:: python

   """When logged in as a Global Administrator"""
   admin.files.download_as_zip('Users/John Smith/My Files/Documents', ['Sample.docx', 'Wizard Of Oz.docx'])

   """When logged in as a tenant user or admin"""
   user.files.download_as_zip('Users/John Smith/My Files/Documents', ['Sample.docx', 'Wizard Of Oz.docx'])

Copy
====

.. automethod:: cterasdk.core.files.browser.FileBrowser.copy
   :noindex:

.. code:: python

   user.files.copy(*['My Files/Documents/Sample.docx', 'My Files/Documents/Burndown.xlsx'], destination='The/quick/brown/fox')


Create Public Link
==================

.. automethod:: cterasdk.core.files.browser.FileBrowser.public_link
   :noindex:

.. code:: python

   """
   Access:
   - RW: Read Write
   - RO: Read Only
   - NA: No Access
   """

   """Create a Read Only public link to a file that expires in 30 days"""

   user.files.public_link('My Files/Documents/Sample.docx')

   """Create a Read Write public link to a folder that expires in 45 days"""

   user.files.public_link('My Files/Documents/Sample.docx', 'RW', 45)

Create Directories
==================

.. automethod:: cterasdk.core.files.browser.CloudDrive.mkdir
   :noindex:

.. code:: python

   """When logged in as a Global Administrator"""
   admin.files.mkdir('Users/John Smith/My Files/Documents')

   """When logged in as a tenant user or admin"""
   user.files.mkdir('My Files/Documents')

.. automethod:: cterasdk.core.files.browser.CloudDrive.makedirs
   :noindex:

.. code:: python

   """When logged in as a Global Administrator"""
   admin.files.makedirs('Users/John Smith/My Files/The/quick/brown/fox')

   """When logged in as a tenant user or admin"""
   user.files.makedirs('The/quick/brown/fox')

Rename
======

.. automethod:: cterasdk.core.files.browser.CloudDrive.rename
   :noindex:

.. code:: python

   """When logged in as a Global Administrator"""
   admin.files.rename('Users/John Smith/My Files/Documents/Sample.docx', 'Wizard Of Oz.docx')

   """When logged in as a tenant user or admin"""
   user.files.makedirs('My Files/Documents/Sample.docx', 'Wizard Of Oz.docx')

Delete
======

.. automethod:: cterasdk.core.files.browser.CloudDrive.delete
   :noindex:

.. code:: python

   """When logged in as a Global Administrator"""
   admin.files.delete(*['Users/John Smith/My Files/Documents/Sample.docx', 'Users/John Smith/My Files/Documents/Wizard Of Oz.docx'])

   """When logged in as a tenant user or admin"""
   user.files.delete(*['My Files/Documents/Sample.docx', 'My Files/Documents/Wizard Of Oz.docx'])

Undelete
========

.. automethod:: cterasdk.core.files.browser.CloudDrive.undelete
   :noindex:

.. code:: python

   """When logged in as a Global Administrator"""
   admin.files.undelete(*['Users/John Smith/My Files/Documents/Sample.docx', 'Users/John Smith/My Files/Documents/Wizard Of Oz.docx'])

   """When logged in as a tenant user or admin"""
   user.files.undelete(*['My Files/Documents/Sample.docx', 'My Files/Documents/Wizard Of Oz.docx'])

Move
====

.. automethod:: cterasdk.core.files.browser.CloudDrive.move
   :noindex:

.. code:: python

   """When logged in as a Global Administrator"""
   admin.files.move(*['Users/John Smith/My Files/Documents/Sample.docx', 'Users/John Smith/My Files/Documents/Wizard Of Oz.docx'], destination='Users/John Smith/The/quick/brown/fox')

   """When logged in as a tenant user or admin"""
   user.files.move(*['My Files/Documents/Sample.docx', 'My Files/Documents/Wizard Of Oz.docx'], destination='The/quick/brown/fox')

Upload
======

.. automethod:: cterasdk.core.files.browser.CloudDrive.upload

.. code:: python

   """When logged in as a Global Administrator"""
   admin.files.upload(r'C:\Users\admin\Downloads\Tree.jpg', 'Users/John Smith/My Files/Images')

   """Uploading as a tenant user or admin"""
   user.files.upload(r'C:\Users\admin\Downloads\Tree.jpg', 'My Files/Images')


Collaboration Shares
====================

.. automethod:: cterasdk.core.files.browser.CloudDrive.share
   :noindex:

.. code:: python

   """
   Share with a local user and a local group.
   - Grant the local user with read only access for 30 days
   - Grant the local group with read write access with no expiration
   """

   alice = core_types.UserAccount('alice')
   engineers = core_types.GroupAccount('Engineers')

   recipients = []

   alice_rcpt = core_types.ShareRecipient.local_user(alice).expire_in(30).read_only()
   engineers_rcpt = core_types.ShareRecipient.local_group(engineering).read_write()

   admin.files.share('Codebase', [alice_rcpt, engineers_rcpt])

..

.. code:: python

   """
   Share with an external recipient
   - Grant the external user with preview only access for 10 days
   """
   jsmith = core_types.ShareRecipient.external('jsmith@hotmail.com').expire_in(10).preview_only()
   admin.files.share('My Files/Projects/2020/ProjectX', [jsmith])

   """
   Share with an external recipient, and require 2 factor authentication
   - Grant the external user with read only access for 5 days, and require 2 factor authentication over e-mail
   """
   jsmith = core_types.ShareRecipient.external('jsmith@hotmail.com', True).expire_in(5).read_only()
   admin.files.share('My Files/Projects/2020/ProjectX', [jsmith])

..

.. code:: python

   """
   Share with a domain groups
   - Grant the Albany domain group with read write access with no expiration
   - Grant the Cleveland domain group with read only access with no expiration
   """
   albany_group = core_types.GroupAccount('Albany', 'ctera.com')
   cleveland_group = core_types.GroupAccount('Cleveland', 'ctera.com')

   albany_rcpt = core_types.ShareRecipient.domain_group(albany_group).read_write()
   cleveland_rcpt = core_types.ShareRecipient.domain_group(cleveland_group).read_only()

   admin.files.share('Cloud/Albany', [albany_rcpt, cleveland_rcpt])

.. automethod:: cterasdk.core.files.browser.CloudDrive.add_share_recipients
   :noindex:

.. note:: if the share recipients provided as an argument already exist, they will be skipped and not updated

.. automethod:: cterasdk.core.files.browser.CloudDrive.remove_share_recipients
   :noindex:

..

.. automethod:: cterasdk.core.files.browser.CloudDrive.unshare
   :noindex:

.. code:: python

   """
   Unshare a file or a folder
   """
   admin.files.unshare('Codebase')
   admin.files.unshare('My Files/Projects/2020/ProjectX')
   admin.files.unshare('Cloud/Albany')


Managing S3 Credentials
=======================

Starting CTERA 8.0, CTERA Portal features programmatic access via the S3 protocol, also known as *CTERA Fusion*
For more information on how to enable CTERA Fusion and the supported extensions of the S3 protocol, please refer to the following `article <https://kb.ctera.com/v1/docs/en/setting-up-access-from-an-s3-browser>`.

The following section includes examples on how to instantiate an S3 client using the Amazon SDK for Python (boto3).

.. code:: python

   credentials = user.credentials.s3.create()  # if logged in as a user
   # credentials = admin.credentials.s3.create(core_types.UserAccount('username', 'domain'))  # if logged in as a Global Admin

   """Instantiate the boto3 client"""
   client = boto3.client(
         's3',
         endpoint_url=https://domain.ctera.com:8443,  # your CTERA Portal tenant domain
         aws_access_key_id=credentials.accessKey,
         aws_secret_access_key=credentials.secretKey,
         verify=False  # disable certificate verification (Optional)
   )

   """List Buckets"""
   response = client.list_buckets()
   for bucket in response['Buckets']:
      print(bucket['Name'])

   """Upload a file"""
   client.upload_file(r'./document.docx', 'my-bucket-name', 'data-management-document.docx')

   """List files"""
   response = client.list_objects_v2(Bucket='my-bucket-name')
   for item in response['Contents']:
      print(item['Key'], item['LastModified'])

   """List files, using Pagination"""
   paginator = client.get_paginator('list_objects_v2')
   for page in paginator.paginate(Bucket='my-bucket-name'):
      for item in page['Contents']:
         print(item['Key'], item['LastModified'])

   """Download a file"""
   client.download_file(r'./data-management-document.docx', 'my-bucket-name', 'data-management-document-copy.docx')

   # for more information, please refer to the Amazon SDK for Python (boto3) documentation.
