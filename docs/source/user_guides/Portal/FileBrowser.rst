************
File Browser
************

.. contents:: Table of Contents

File Browser
------------

List
====

.. automethod:: cterasdk.core.files.browser.FileBrowser.ls
   :noindex:

.. code:: python

   file_browser.ls('')  # List the contents of the Cloud Drive

   file_browser.ls('My Files')  # List the contents of the 'My Files' folder

   file_browser.ls('My Files', True)  # Include deleted files

.. automethod:: cterasdk.core.files.browser.FileBrowser.walk
   :noindex:

.. code:: python

   file_browser.walk('My Files')

Download
========

.. automethod:: cterasdk.core.files.browser.FileBrowser.download
   :noindex:

.. code:: python

   file_browser.download('My Files/Documents/Sample.docx')

Copy
====

.. automethod:: cterasdk.core.files.browser.FileBrowser.copy
   :noindex:

.. code:: python

   file_browser.copy('My Files/Documents/Sample.docx', 'The/quick/brown/fox')

.. automethod:: cterasdk.core.files.browser.FileBrowser.copy_multi
   :noindex:

.. code:: python

   file_browser.copy_multi(['My Files/Documents/Sample.docx', 'My Files/Documents/Burndown.xlsx'], 'The/quick/brown/fox')

Create Public Link
==================

.. automethod:: cterasdk.core.files.browser.FileBrowser.mklink
   :noindex:

.. code:: python

   """
   Access:
   - RW: Read Write
   - RO: Read Only
   - NA: No Access
   """

   """Create a Read Only public link to a file that expires in 30 days"""

   file_browser.mklink('My Files/Documents/Sample.docx')

   """Create a Read Write public link to a folder that expires in 45 days"""

   file_browser.mklink('My Files/Documents/Sample.docx', 'RW', 45)

.. warning:: you cannot use this tool to create read write public links to files.

Cloud Drive
-----------

The CloudDrive class is a subclass to :py:class:`cterasdk.common.files.browser.FileBrowser` providing file access to the user's Cloud Drive

.. code:: python

   from getpass import getpass

   """Accessing Cloud Drive Files and Folders as a Global Administrator"""
   admin = GlobalAdmin('portal.ctera.com')  # logging in to /admin
   admin.login('admin', getpass())
   file_browser = admin.files # the field is an instance of CloudDrive class object

   """Accessing Cloud Drive Files and Folders as a Tenant User Account"""
   user = ServicesPortal('portal.ctera.com')  # logging in to /ServicesPortal
   user.login('bwayne', getpass())
   file_browser = user.files # the field is an instance of CloudDrive class object

Create Directory
================

.. automethod:: cterasdk.core.files.browser.CloudDrive.mkdir
   :noindex:

.. code:: python

   file_browser.mkdir('My Files/Documents')

   file_browser.mkdir('The/quick/brown/fox', recurse = True)

Rename
======

.. automethod:: cterasdk.core.files.browser.CloudDrive.rename
   :noindex:

.. code:: python

   file_browser.rename('My Files/Documents/Sample.docx', 'Wizard Of Oz.docx')

Delete
======
.. automethod:: cterasdk.core.files.browser.CloudDrive.delete
   :noindex:

.. code:: python

   file_browser.delete('My Files/Documents/Sample.docx')

.. automethod:: cterasdk.core.files.browser.CloudDrive.delete_multi
   :noindex:

.. code:: python

   file_browser.delete_multi('My Files/Documents/Sample.docx', 'The/quick/brown/fox')

Undelete
========

.. automethod:: cterasdk.core.files.browser.CloudDrive.undelete
   :noindex:

.. code:: python

   file_browser.undelete('My Files/Documents/Sample.docx')

.. automethod:: cterasdk.core.files.browser.CloudDrive.undelete_multi
   :noindex:

.. code:: python

   file_browser.undelete_multi('My Files/Documents/Sample.docx', 'The/quick/brown/fox')

Move
====

.. automethod:: cterasdk.core.files.browser.CloudDrive.move
   :noindex:

.. code:: python

   file_browser.move('My Files/Documents/Sample.docx', 'The/quick/brown/fox')

.. automethod:: cterasdk.core.files.browser.CloudDrive.move_multi
   :noindex:

.. code:: python

   file_browser.move_multi(['My Files/Documents/Sample.docx', 'My Files/Documents/Burndown.xlsx'], 'The/quick/brown/fox')

Upload
======

.. automethod:: cterasdk.core.files.browser.CloudDrive.upload

.. code:: python

   """
   Upload the 'Tree.jpg' file as an End User to 'Forest' directory
   """
   file_browser.files.upload(r'C:\Users\BruceWayne\Downloads\Tree.jpg', 'Images/Forest')

   """
   Upload the 'Tree.jpg' file as an Administrator to an End User's Cloud Drive
   """
   file_browser.files.upload(r'C:\Users\Administrator\Downloads\Tree.jpg', 'Bruce Wayne/Images/Forest')


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

   alice = portal_types.UserAccount('alice')
   engineers = portal_types.GroupAccount('Engineers')

   recipients = []

   alice_rcpt = portal_types.ShareRecipient.local_user(alice).expire_in(30).read_only()
   engineers_rcpt = portal_types.ShareRecipient.local_group(engineering).read_write()

   file_browser.share('Codebase', [alice_rcpt, engineers_rcpt])

..

.. code:: python

   """
   Share with an external recipient
   - Grant the external user with preview only access for 10 days
   """
   jsmith = portal_types.ShareRecipient.external('jsmith@hotmail.com').expire_in(10).preview_only())
   file_browser.share('My Files/Projects/2020/ProjectX', [jsmith])

   """
   Share with an external recipient, and require 2 factor authentication
   - Grant the external user with read only access for 5 days, and require 2 factor authentication over e-mail
   """
   jsmith = portal_types.ShareRecipient.external('jsmith@hotmail.com', True).expire_in(5).read_only())
   file_browser.share('My Files/Projects/2020/ProjectX', [jsmith])

..

.. code:: python

   """
   Share with a domain groups
   - Grant the Albany domain group with read write access with no expiration
   - Grant the Cleveland domain group with read only access with no expiration
   """
   albany_group = portal_types.GroupAccount('Albany', 'ctera.com')
   cleveland_group = portal_types.GroupAccount('Cleveland', 'ctera.com')

   albany_rcpt = portal_types.ShareRecipient.domain_group(albany_group).read_write()
   cleveland_rcpt = portal_types.ShareRecipient.domain_group(cleveland_group).read_only()

   file_browser.share('Cloud/Albany', [albany_rcpt, cleveland_rcpt])

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
   file_browser.unshare('Codebase')
   file_browser.unshare('My Files/Projects/2020/ProjectX')
   file_browser.unshare('Cloud/Albany')

Backups
-------

The Backups class is a subclass to :py:class:`cterasdk.common.files.browser.FileBrowser` providing access to files stored in backup folders

.. code:: python

   from getpass import getpass

   """Accessing Backups as a Global Administrator"""
   admin = GlobalAdmin('portal.ctera.com')  # logging in to /admin
   admin.login('admin', getpass())
   file_browser = admin.files # the field is an instance of Backups class object

   """Accessing Backups as a Tenant User Account"""
   user = ServicesPortal('portal.ctera.com')  # logging in to /ServicesPortal
   user.login('bwayne', getpass())
   file_browser = user.backups  # the field is an instance of Backups class object

CTERA Fusion (S3)
-----------------

Starting CTERA 8.0, CTERA Portal features programmatic access via the S3 protocol, also known as *CTERA Fusion* 
For more information on how to enable CTERA Fusion and the supported extensions of the S3 protocol, please refer to the following `article <https://kb.ctera.com/v1/docs/en/setting-up-access-from-an-s3-browser>`.

The following section includes examples on how to instantiate an S3 client using the Amazon SDK for Python (boto3).

.. code:: python

   credentials = user.credentials.s3.create()  # if logged in as a user
   # credentials = admin.credentials.s3.create(portal_types.UserAccount('username', 'domain'))  # if logged in as a Global Admin

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