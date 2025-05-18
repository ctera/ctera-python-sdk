============
File Browser
============

Synchronous API
===============

List
----

.. automethod:: cterasdk.edge.files.browser.FileBrowser.listdir
   :noindex:

.. code:: python

   for item in edge.files.listdir('/'):
       print(item.name, item.fullpath)

Download
--------

.. automethod:: cterasdk.edge.files.browser.FileBrowser.download
   :noindex:

.. code:: python

   edge.files.download('cloud/users/Service Account/My Files/Documents/Sample.docx')

.. automethod:: cterasdk.edge.files.browser.FileBrowser.download_many
   :noindex:

.. code:: python

   edge.files.download_many('network-share/docs', ['Sample.docx', 'Summary.xlsx'])

Create Directory
----------------

.. automethod:: cterasdk.edge.files.browser.FileBrowser.mkdir
   :noindex:

.. code:: python

   edge.files.mkdir('cloud/users/Service Account/My Files/Documents')


.. automethod:: cterasdk.edge.files.browser.FileBrowser.makedirs
   :noindex:

.. code:: python

   edge.files.makedirs('cloud/users/Service Account/My Files/The/quick/brown/fox')


Copy
----

.. automethod:: cterasdk.edge.files.browser.FileBrowser.copy
   :noindex:

.. code:: python

   """
   Copy the 'Documents' folder from Bruce Wayne to Alice Wonderland
   The full path of the documents folder after the copy: 'cloud/users/Alice Wonderland/My Files/Documents'
   """
   edge.files.copy('cloud/users/Bruce Wayne/My Files/Documents', destination='cloud/users/Alice Wonderland/My Files')

   """Copy the file Summary.xlsx to another directory, and overwrite on conflict"""
   edge.files.copy('cloud/users/Bruce Wayne/My Files/Summary.xlsx', destination='cloud/users/Bruce Wayne/Spreadsheets', overwrite=True)


Move
----

.. automethod:: cterasdk.edge.files.browser.FileBrowser.move
   :noindex:

.. code:: python

   """
   Move the 'Documents' folder from Bruce Wayne to Alice Wonderland
   The full path of the documents folder after the move: 'cloud/users/Alice Wonderland/My Files/Documents'
   """
   edge.files.move('cloud/users/Bruce Wayne/My Files/Documents', destination='cloud/users/Alice Wonderland/My Files')

   """Move the file Summary.xlsx to another directory, and overwrite on conflict"""
   edge.files.move('cloud/users/Bruce Wayne/My Files/Summary.xlsx', destination='cloud/users/Bruce Wayne/Spreadsheets', overwrite=True)

Delete
------

.. automethod:: cterasdk.edge.files.browser.FileBrowser.delete
   :noindex:

.. code:: python

   edge.files.delete('cloud/users/Service Account/My Files/Documents')


Asynchronous API
================

Asynchronous API
================

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.handle
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.handle_many
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.download
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.download_many
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.listdir
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.copy
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.FileBrowser.move
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.CloudDrive.upload
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.CloudDrive.upload_file
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.CloudDrive.mkdir
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.CloudDrive.makedirs
   :noindex:

.. automethod:: cterasdk.asynchronous.edge.files.browser.CloudDrive.delete
   :noindex: