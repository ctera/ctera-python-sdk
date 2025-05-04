============
File Browser
============

This article outlines the file-browser APIs available in the CTERA Portal, enabling programmatic access to files and directories.

The API supports both **synchronous** and **asynchronous** implementations, allowing developers to choose the most suitable model for their integration use case—whether real-time interactions or background processing.


Synchronous API
===============


User Roles
----------

The file access APIs are available to the following user roles:

- **Global Administrators** with the `Access End User Folders` permission enabled.
- **Team Portal Administrators** with the `Access End User Folders` permission enabled.
- **End Users**, accessing their personal cloud drive folders.

For more information, See: `Customizing Administrator Roles <https://kb.ctera.com/docs/customizing-administrator-roles-2>`_

List
----

.. automethod:: cterasdk.core.files.browser.FileBrowser.listdir
   :noindex:

.. code:: python

   """List directories as a Global Administrator"""
   with GlobalAdmin('tenant.ctera.com') as admin:
      admin.login('admin-user', 'admin-pass')

      """List all sub-directories"""
      for f in admin.files.listdir('Users/John Smith/My Files'):
          if f.isFolder:
              print({
                  f.name,
                  f.href,
                  f.permalink  # a URL that links directly to a specific file
              })

.. code:: python

   """List directories as a Team Portal Administrator or End User"""
   with ServicesPortal('tenant.ctera.com') as user:
      user.login('username', 'user-password')
      for f in user.files.listdir('My Files/Documents'):
          if not f.isFolder:
              print({
                  f.name,
                  f.href,
                  f.size,
                  f.lastmodified,
                  f.permalink  # a URL that links directly to a specific file
              })

      """List all deleted files"""
      deleted_files = [f.href for f in user.files.listdir('My Files/Documents', include_deleted=True) if f.isDeleted]
      print(deleted_files)

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

Versions
--------

.. automethod:: cterasdk.core.files.browser.FileBrowser.versions
   :noindex:

.. code:: python

   """When logged in as a Global Administrator"""
   versions = admin.files.versions('Users/John Smith/My Files/Documents')
   for version in versions:
       if not version.current:
           for item in admin.files.listdir(version):  # list items from previous versions
               print(version.calculatedTimestamp, item.name)


   """When logged in as a Team Portal Administrator End User"""
   versions = user.files.versions('My Files/Documents')
   for version in versions:
       if not version.current:
           for item in user.files.listdir(version):  # list items from previous versions
               print(version.calculatedTimestamp, item.name)

Download
--------

.. automethod:: cterasdk.core.files.browser.FileBrowser.download
   :noindex:

.. code:: python

   """When logged in as a Global Administrator"""
   admin.files.download('Users/John Smith/My Files/Documents/Sample.docx')

   """When logged in as a Team Portal Administrator End User"""
   user.files.download('My Files/Documents/Sample.docx')

.. automethod:: cterasdk.core.files.browser.FileBrowser.download_many
   :noindex:

.. code:: python

   """When logged in as a Global Administrator"""
   admin.files.download_many('Users/John Smith/My Files/Documents', ['Sample.docx', 'Wizard Of Oz.docx'])

   """When logged in as a Team Portal Administrator End User"""
   user.files.download_many('My Files/Documents', ['Sample.docx', 'Wizard Of Oz.docx'])

Copy
----

.. automethod:: cterasdk.core.files.browser.FileBrowser.copy
   :noindex:

.. code:: python

   """When logged in as a Team Portal Administrator End User"""
   user.files.copy(*['My Files/Documents/Sample.docx', 'My Files/Documents/Burndown.xlsx'], destination='The/quick/brown/fox')


Create Public Link
------------------

.. automethod:: cterasdk.core.files.browser.FileBrowser.public_link
   :noindex:

.. code:: python

   """
   Access:
   - RW: Read Write
   - RO: Read Only
   - NA: No Access
   """

   """When logged in as a Team Portal Administrator End User"""
   """Create a Read Only public link to a file that expires in 30 days"""
   user.files.public_link('My Files/Documents/Sample.docx')

   """When logged in as a Team Portal Administrator End User"""
   """Create a Read Write public link to a folder that expires in 45 days"""
   user.files.public_link('My Files/Documents/Sample.docx', 'RW', 45)


Get Permalink
-------------

.. automethod:: cterasdk.core.files.browser.FileBrowser.permalink
   :noindex:

.. code:: python

   """When logged in as a Team Portal Administrator End User"""
   """Create permalink to a file"""
   user.files.permalink('My Files/Documents/Sample.docx')

   """When logged in as a Team Portal Administrator End User"""
   """Create permalink to a folder"""
   user.files.permalink('My Files/Documents')


Create Directories
------------------

.. automethod:: cterasdk.core.files.browser.CloudDrive.mkdir
   :noindex:

.. code:: python

   """When logged in as a Global Administrator"""
   admin.files.mkdir('Users/John Smith/My Files/Documents')

   """When logged in as a Team Portal Administrator End User"""
   user.files.mkdir('My Files/Documents')

.. automethod:: cterasdk.core.files.browser.CloudDrive.makedirs
   :noindex:

.. code:: python

   """When logged in as a Global Administrator"""
   admin.files.makedirs('Users/John Smith/My Files/The/quick/brown/fox')

   """When logged in as a Team Portal Administrator End User"""
   user.files.makedirs('The/quick/brown/fox')

Rename
------

.. automethod:: cterasdk.core.files.browser.CloudDrive.rename
   :noindex:

.. code:: python

   """When logged in as a Global Administrator"""
   admin.files.rename('Users/John Smith/My Files/Documents/Sample.docx', 'Wizard Of Oz.docx')

   """When logged in as a tenant user or admin"""
   user.files.makedirs('My Files/Documents/Sample.docx', 'Wizard Of Oz.docx')

Delete
------

.. automethod:: cterasdk.core.files.browser.CloudDrive.delete
   :noindex:

.. code:: python

   """When logged in as a Global Administrator"""
   admin.files.delete(*['Users/John Smith/My Files/Documents/Sample.docx', 'Users/John Smith/My Files/Documents/Wizard Of Oz.docx'])

   """When logged in as a Team Portal Administrator End User"""
   user.files.delete(*['My Files/Documents/Sample.docx', 'My Files/Documents/Wizard Of Oz.docx'])

Undelete
--------

.. automethod:: cterasdk.core.files.browser.CloudDrive.undelete
   :noindex:

.. code:: python

   """When logged in as a Global Administrator"""
   admin.files.undelete(*['Users/John Smith/My Files/Documents/Sample.docx', 'Users/John Smith/My Files/Documents/Wizard Of Oz.docx'])

   """When logged in as a Team Portal Administrator End User"""
   user.files.undelete(*['My Files/Documents/Sample.docx', 'My Files/Documents/Wizard Of Oz.docx'])

Move
----

.. automethod:: cterasdk.core.files.browser.CloudDrive.move
   :noindex:

.. code:: python

   """When logged in as a Global Administrator"""
   admin.files.move(*['Users/John Smith/My Files/Documents/Sample.docx', 'Users/John Smith/My Files/Documents/Wizard Of Oz.docx'], destination='Users/John Smith/The/quick/brown/fox')

   """When logged in as a Team Portal Administrator End User"""
   user.files.move(*['My Files/Documents/Sample.docx', 'My Files/Documents/Wizard Of Oz.docx'], destination='The/quick/brown/fox')

Upload
------

.. automethod:: cterasdk.core.files.browser.CloudDrive.upload

.. code:: python

   """When logged in as a Global Administrator"""
   admin.files.upload(r'C:\Users\admin\Downloads\Tree.jpg', 'Users/John Smith/My Files/Images')

   """When logged in as a Team Portal Administrator End User"""
   user.files.upload(r'C:\Users\admin\Downloads\Tree.jpg', 'My Files/Images')


Collaboration Shares
--------------------

.. automethod:: cterasdk.core.files.browser.CloudDrive.share
   :noindex:

.. code:: python

   """When logged in as a Team Portal Administrator End User"""

   """
   Share with a local user and a local group.
   - Grant the local user with read only access for 30 days
   - Grant the local group with read write access with no expiration
   """

   alice = core_types.UserAccount('alice')
   engineers = core_types.GroupAccount('Engineers')

   alice_rcpt = core_types.ShareRecipient.local_user(alice).expire_in(30).read_only()
   engineers_rcpt = core_types.ShareRecipient.local_group(engineers).read_write()

   user.files.share('Codebase', [alice_rcpt, engineers_rcpt])

..

.. code:: python

   """When logged in as a Team Portal Administrator End User"""

   """
   Share with an external recipient
   - Grant the external user with preview only access for 10 days
   """
   jsmith = core_types.ShareRecipient.external('jsmith@hotmail.com').expire_in(10).preview_only()
   user.files.share('My Files/Projects/2020/ProjectX', [jsmith])

   """
   Share with an external recipient, and require 2 factor authentication
   - Grant the external user with read only access for 5 days, and require 2 factor authentication over e-mail
   """
   jsmith = core_types.ShareRecipient.external('jsmith@hotmail.com', True).expire_in(5).read_only()
   user.files.share('My Files/Projects/2020/ProjectX', [jsmith])

..

.. code:: python

   """When logged in as a Team Portal Administrator End User"""

   """
   Share with a domain groups
   - Grant the Albany domain group with read write access with no expiration
   - Grant the Cleveland domain group with read only access with no expiration
   """
   albany_group = core_types.GroupAccount('Albany', 'ctera.com')
   cleveland_group = core_types.GroupAccount('Cleveland', 'ctera.com')

   albany_rcpt = core_types.ShareRecipient.domain_group(albany_group).read_write()
   cleveland_rcpt = core_types.ShareRecipient.domain_group(cleveland_group).read_only()

   user.files.share('Cloud/Albany', [albany_rcpt, cleveland_rcpt])

.. automethod:: cterasdk.core.files.browser.CloudDrive.add_share_recipients
   :noindex:

.. code:: python

   """When logged in as a Team Portal Administrator End User"""

   """
   Add collaboration shares members.

   - Grant the 'Engineering' local group with read-write permission
   """
   engineering = core_types.GroupAccount('Engineering')
   engineering_rcpt = core_types.ShareRecipient.local_group(engineering).read_write()
   user.files.add_share_recipients('My Files/Projects/2020/ProjectX', [engineering_rcpt])

.. note:: if the share recipients provided as an argument already exist, they will be skipped and not updated

.. automethod:: cterasdk.core.files.browser.CloudDrive.remove_share_recipients
   :noindex:

.. code:: python

   """When logged in as a Team Portal Administrator End User"""

   """Remove 'Alice' and 'Engineering' from the List of Recipients"""
   alice = core_types.UserAccount('alice')
   engineering = core_types.GroupAccount('Engineering')
   user.files.remove_share_recipients('My Files/Projects/2020/ProjectX', [alice, engineering])

.. automethod:: cterasdk.core.files.browser.CloudDrive.unshare
   :noindex:

.. code:: python

   """
   Unshare a file or a folder
   """
   user.files.unshare('Codebase')
   user.files.unshare('My Files/Projects/2020/ProjectX')
   user.files.unshare('Cloud/Albany')


Managing S3 Credentials
-----------------------

Starting CTERA 8.0, CTERA Portal features programmatic access via the S3 protocol, also known as *CTERA Fusion*
For more information on how to enable CTERA Fusion and the supported extensions of the S3 protocol, please refer to the following `article <https://kb.ctera.com/v1/docs/en/setting-up-access-from-an-s3-browser>`_

The following section includes examples on how to instantiate an S3 client using the Amazon SDK for Python `boto3 <https://pypi.org/project/boto3/>`_

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

.. automethod:: cterasdk.asynchronous.core.files.browser.FileBrowser.move
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


.. code:: python

   """Access a Global Administrator"""
   async with AsyncGlobalAdmin('global.ctera.com') as admin:
       await admin.login('username', 'password')
       await admin.portals.browse('corp')  # access files in the 'corp' Team Portal tenant

       """Create directories recursively"""
       await admin.files.makedirs('Users/John Smith/My Files/the/quick/brown/fox')

       """Create a 'Documents' directory"""
       await admin.files.mkdir('Users/John Smith/Documents')

       """Walk 'John Smith's My Files directory"""
       async for i in admin.files.walk('Users/John Smith/My Files'):
           print(i.name, i.size, i.lastmodified, i.permalink)

       """List all files in a directory"""
       documents = [i.name async for i in admin.files.listdir('Users/John Smith/Documents') if i.isfile]

       """Rename a directory"""
       await admin.files.rename('Users/John Smith/Documents', 'Documents360')

       """Download"""
       await admin.files.download('Users/John Smith/My Files/Sunrise.png')
       await admin.files.download('Users/John Smith/My Files/Sunrise.png', 'c:/users/jsmith/downloads/Patagonia.png')

       await admin.files.download_many('Users/John Smith/Pictures', ['Sunrise.png', 'Gelato.pptx'])
       await admin.files.download_many('Users/John Smith/Pictures', ['Sunrise.png', 'Gelato.pptx'], 'c:/users/jsmith/downloads/Images.zip')

       """Upload"""
       await admin.files.upload_file('c:/users/jsmith/downloads/Sunset.png', '/Users/John Smith/Pictures')

       """Public Link"""
       url = await admin.files.public_link('Users/John Smith/Pictures/Sunrise.png')
       print(url)

.. code:: python

   """Access a Team Portal Administrator or End User"""
   async with AsyncservicesPortal('tenant.ctera.com') as user:
       await user.login('username', 'password')

       """Create directories as an End User"""
       await user.files.makedirs('My Files/the/quick/brown/fox')  # Create a directory in your own account

       """Create directories as Team Portal Administrator"""
       await user.files.makedirs('Users/John Smith/My Files/the/quick/brown/fox')  # Create a directory in a user's account 
