============
File Browser
============

Download
========

.. automethod:: cterasdk.edge.files.browser.FileBrowser.download
   :noindex:

.. code:: python

   edge.files.download('cloud/users/Service Account/My Files/Documents/Sample.docx')

Create Directory
================

.. automethod:: cterasdk.edge.files.browser.FileBrowser.mkdir
   :noindex:

.. code:: python

   edge.files.mkdir('cloud/users/Service Account/My Files/Documents')


.. automethod:: cterasdk.edge.files.browser.FileBrowser.makedirs
   :noindex:

.. code:: python

   edge.files.makedirs('cloud/users/Service Account/My Files/The/quick/brown/fox')


Copy
====

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
====

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
======

.. automethod:: cterasdk.edge.files.browser.FileBrowser.delete
   :noindex:

.. code:: python

   edge.files.delete('cloud/users/Service Account/My Files/Documents')
