============
File Browser
============

Preface: Authentication
=======================

Before using the Edge Filer API, you need to authenticate with your Edge device. Below are examples for synchronous and asynchronous usage.

Synchronous login
-----------------

Set ``cterasdk.settings.edge.syn.settings.connector.ssl = False`` to disable SSL verification.

.. code:: python

   from cterasdk.edge import Edge

   username = "admin"
   password = "secret"

   with Edge('172.54.3.149') as edge:
       edge.login(username, password)
       # Now you can access files via edge.files

Asynchronous login
------------------

Set ``cterasdk.settings.edge.asyn.settings.connector.ssl = False`` to disable SSL verification.

.. code:: python

   import asyncio
   from cterasdk.asynchronous.edge import AsyncEdge

   async def main():
      username = "admin"
      password = "secret"

      async with AsyncEdge('172.54.3.149') as edge:
         await edge.login(username, password)
         # Now you can access files via edge.files

   asyncio.run(main())

Synchronous API
===============

Listing Files and Directories
-----------------------------

.. automethod:: cterasdk.edge.files.browser.FileBrowser.listdir
   :noindex:

.. code:: python

   # List contents of the root directory
   for item in edge.files.listdir('/'):
       print(item.name, str(item), item.is_dir, item.size)

.. automethod:: cterasdk.edge.files.browser.FileBrowser.walk
   :noindex:

.. code:: python

   # Walk through all files and directories recursively
   for item in edge.files.walk('/'):
       print(item.name, str(item), item.is_dir, item.size)

Inspecting Files
----------------

.. automethod:: cterasdk.edge.files.browser.FileBrowser.properties
   :noindex:

.. code:: python

   # Get file or directory properties
   resource = edge.files.properties('cloud/users/Service Account/My Files/Keystone Project.docx')
   print(resource.name, str(resource), resource.is_dir, resource.size, resource.last_modified)

.. automethod:: cterasdk.edge.files.browser.FileBrowser.exists
   :noindex:

.. code:: python

   # Check if a file exists
   if edge.files.exists('cloud/users/Service Account/My Files/Keystone Project.docx'):
       print("File exists")

File Handles
------------

.. automethod:: cterasdk.edge.files.browser.FileBrowser.handle
   :noindex:

.. code:: python

   # Get a handle to a single file
   handle = edge.files.handle('cloud/users/Service Account/My Files/Keystone Project.docx')

.. automethod:: cterasdk.edge.files.browser.FileBrowser.handle_many
   :noindex:

.. code:: python

   # Get a handle to multiple files/folders as a ZIP
   handle = edge.files.handle_many('cloud/users/Service Account/My Files', 'Keystone Project.docx', 'Keystone Model.docx')

Downloading Files
-----------------

.. automethod:: cterasdk.edge.files.browser.FileBrowser.download
   :noindex:

.. code:: python

   # Download a single file to default location
   local_path = edge.files.download('cloud/users/Service Account/My Files/Keystone Project.docx')

.. automethod:: cterasdk.edge.files.browser.FileBrowser.download_many
   :noindex:

.. code:: python

   # Download multiple files as a ZIP archive
   zip_path = edge.files.download_many('network-share/docs', ['Keystone Project.docx', 'Keystone Model.docx'])

Creating Directories
--------------------

.. automethod:: cterasdk.edge.files.browser.FileBrowser.mkdir
   :noindex:

.. code:: python

   # Create a single directory
   edge.files.mkdir('cloud/users/Service Account/My Files/Documents')

.. automethod:: cterasdk.edge.files.browser.FileBrowser.makedirs
   :noindex:

.. code:: python

   # Create directories recursively
   edge.files.makedirs('cloud/users/Service Account/My Files/The/quick/brown/fox')

File Operations: Copy, Move, Rename, Delete
-------------------------------------------

.. automethod:: cterasdk.edge.files.browser.FileBrowser.copy
   :noindex:

.. code:: python

   # Copy a file to a directory
   edge.files.copy('Keystone-Corporation/Project Keystone.docx', destination='Keystone-Coporation/Documents')

   # Copy a file and rename the file at the destination
   edge.files.copy('Keystone-Corporation/Project Keystone.docx', destination='Keystone-Coporation/Documents/Keystone 2026.docx')

   # Copy a file to a directory and overwrite if it exists
   edge.files.copy('Keystone-Corporation/Project Keystone.docx', destination='Keystone-Coporation/Documents', overwrite=True)

.. automethod:: cterasdk.edge.files.browser.FileBrowser.move
   :noindex:

.. code:: python

   # Move a file to a directory
   edge.files.move('Keystone-Corporation/Project Keystone.docx', destination='Keystone-Coporation/Documents')

   # Move a file and rename the file at the destination
   edge.files.move('Keystone-Corporation/Project Keystone.docx', destination='Keystone-Coporation/Documents/Keystone 2026.docx')

   # Move a file to a directory and overwrite if it exists
   edge.files.move('Keystone-Corporation/Project Keystone.docx', destination='Keystone-Coporation/Documents', overwrite=True)

.. automethod:: cterasdk.edge.files.browser.FileBrowser.rename
   :noindex:

.. code:: python

   # Rename a file or directory
   edge.files.rename('Keystone-Corporation/Project Keystone.docx', 'Keystone 2026.docx')

.. automethod:: cterasdk.edge.files.browser.FileBrowser.delete
   :noindex:

.. code:: python

   # Delete a file or directory
   edge.files.delete('Keystone-Corporation/Project Keystone.docx')

Uploading Files
---------------

.. automethod:: cterasdk.edge.files.browser.FileBrowser.upload
   :noindex:

.. code:: python

   # Upload from file handle
   with open('Keystone Project.docx', 'rb') as f:
       remote_path = edge.files.upload('cloud/users/Service Account/My Files/Keystone Project.docx', f)

   # Upload from string or bytes
   remote_path = edge.files.upload('cloud/users/Service Account/My Files/Keystone Notes.txt', 'File contents here')

.. automethod:: cterasdk.edge.files.browser.FileBrowser.upload_file
   :noindex:

.. code:: python

   # Upload from a local path to a directory
   remote_path = edge.files.upload_file('./Keystone Project.docx', 'cloud/users/Service Account/My Files')

   # Upload from a local path and rename the file at the destination
   remote_path = edge.files.upload_file('./Keystone Project.docx', 'cloud/users/Service Account/My Files/Keystone 2026.docx')

Asynchronous API
================

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.listdir
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.walk
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.handle
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.handle_many
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.download
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.download_many
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.upload
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.upload_file
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.mkdir
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.makedirs
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.copy
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.move
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.rename
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.delete
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.exists
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.properties
   :noindex:
