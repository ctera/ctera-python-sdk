************
File Browser
************

.. contents:: Table of Contents

List
====

.. automethod:: cterasdk.core.files.browser.FileBrowser.ls
   :noindex:

.. code:: python

   file_browser.ls('')

   file_browser.ls('My Files')

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

Create Directory
================

.. automethod:: cterasdk.core.files.browser.FileBrowser.mkdir
   :noindex:

.. code:: python

   file_browser.mkdir('My Files/Documents')

   file_browser.mkdir('The/quick/brown/fox', recurse = True)

Rename
======

.. automethod:: cterasdk.core.files.browser.FileBrowser.rename
   :noindex:

.. code:: python

   file_browser.rename('My Files/Documents/Sample.docx', 'Wizard Of Oz.docx')

Delete
======
.. automethod:: cterasdk.core.files.browser.FileBrowser.delete
   :noindex:

.. code:: python

   file_browser.delete('My Files/Documents/Sample.docx')

.. automethod:: cterasdk.core.files.browser.FileBrowser.delete_multi
   :noindex:

.. code:: python

   file_browser.delete_multi('My Files/Documents/Sample.docx', 'The/quick/brown/fox')

Recover
=======

.. automethod:: cterasdk.core.files.browser.FileBrowser.undelete
   :noindex:

.. code:: python

   file_browser.undelete('My Files/Documents/Sample.docx')

.. automethod:: cterasdk.core.files.browser.FileBrowser.undelete_multi
   :noindex:

.. code:: python

   file_browser.undelete_multi('My Files/Documents/Sample.docx', 'The/quick/brown/fox')

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

Move
====

.. automethod:: cterasdk.core.files.browser.FileBrowser.move
   :noindex:

.. code:: python

   file_browser.move('My Files/Documents/Sample.docx', 'The/quick/brown/fox')

.. automethod:: cterasdk.core.files.browser.FileBrowser.move_multi
   :noindex:

.. code:: python

   file_browser.move_multi(['My Files/Documents/Sample.docx', 'My Files/Documents/Burndown.xlsx'], 'The/quick/brown/fox')

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
