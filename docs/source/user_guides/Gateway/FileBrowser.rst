************
File Browser
************

.. contents:: Table of Contents

Obtaining Access to the Gateway's File System
---------------------------------------------

.. code:: python

   filer = Gateway('vGateway-0dbc')

   filer.login('USERNAME', 'PASSWORD')

   file_browser = filer.files # the field is an instance of FileBrowser class object

List
====
.. autofunction:: cterasdk.edge.files.browser.FileBrowser.ls
   :noindex:

Download
========
.. autofunction:: cterasdk.edge.files.browser.FileBrowser.download
   :noindex:

.. code:: python

   file_browser.download('cloud/users/Service Account/My Files/Documents/Sample.docx')

Create Directory
================
.. autofunction:: cterasdk.edge.files.browser.FileBrowser.mkdir
   :noindex:

.. code:: python

   file_browser.mkdir('cloud/users/Service Account/My Files/Documents')

   file_browser.mkdir('cloud/users/Service Account/My Files/The/quick/brown/fox', recurse = True)

Delete
======
.. autofunction:: cterasdk.edge.files.browser.FileBrowser.delete
   :noindex:

.. code:: python

   file_browser.delete('cloud/users/Service Account/My Files/Documents')
