************
File Browser
************

.. contents:: Table of Contents

Edge Filer File Access
----------------------

.. code:: python

   filer = Edge('vGateway-0dbc')
   filer.login('USERNAME', 'PASSWORD')
   file_browser = filer.files  # the field is an instance of FileBrowser class object


Download
========

.. automethod:: cterasdk.edge.files.browser.FileBrowser.download
   :noindex:

.. code:: python

   file_browser.download('cloud/users/Service Account/My Files/Documents/Sample.docx')


Create Directory
================

.. automethod:: cterasdk.edge.files.browser.FileBrowser.mkdir
   :noindex:

.. code:: python

   file_browser.mkdir('cloud/users/Service Account/My Files/Documents')


.. automethod:: cterasdk.edge.files.browser.FileBrowser.makedirs
   :noindex:

.. code:: python

   file_browser.makedirs('cloud/users/Service Account/My Files/The/quick/brown/fox')


Copy
====
.. automethod:: cterasdk.edge.files.browser.FileBrowser.copy
   :noindex:

.. code:: python

   """
   Copy the 'Documents' folder from Bruce Wayne to Alice Wonderland
   The full path of the documents folder after the copy: 'cloud/users/Alice Wonderland/My Files/Documents'
   """
   file_browser.copy('cloud/users/Bruce Wayne/My Files/Documents', 'cloud/users/Alice Wonderland/My Files')

   """Copy the file Summary.xlsx to another directory, and overwrite on conflict"""
   file_browser.copy('cloud/users/Bruce Wayne/My Files/Summary.xlsx', 'cloud/users/Bruce Wayne/Spreadsheets', True)


Move
====
.. automethod:: cterasdk.edge.files.browser.FileBrowser.move
   :noindex:

.. code:: python

   """
   Move the 'Documents' folder from Bruce Wayne to Alice Wonderland
   The full path of the documents folder after the move: 'cloud/users/Alice Wonderland/My Files/Documents'
   """
   file_browser.move('cloud/users/Bruce Wayne/My Files/Documents', 'cloud/users/Alice Wonderland/My Files')

   """Move the file Summary.xlsx to another directory, and overwrite on conflict"""
   file_browser.move('cloud/users/Bruce Wayne/My Files/Summary.xlsx', 'cloud/users/Bruce Wayne/Spreadsheets', True)

Delete
======
.. automethod:: cterasdk.edge.files.browser.FileBrowser.delete
   :noindex:

.. code:: python

   file_browser.delete('cloud/users/Service Account/My Files/Documents')
