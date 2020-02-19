************
File Browser
************

.. contents:: Table of Contents

Obtaining Access to the File System
-----------------------------------

.. code:: python

   """Instantiate a file browser as a Global Admin"""

   admin = GlobalAdmin('chopin.ctera.com')
   
   admin.login('USERNAME', 'PASSWORD')
   
   file_browser = admin.files()
   
   """Instantiate a file browser as an End User or a Team Portal admin"""

   user = ServicesPortal('chopin.ctera.com')
   
   user.login('USERNAME', 'PASSWORD')
   
   file_browser = user.files()

List
====

.. py:method:: FileBrowser.ls(path)

   List a directory.
   
   :param path: directory path
   :type path: str

.. code:: python
   
   file_browser.ls('')
   
   file_browser.ls('My Files')
   
.. py:method:: FileBrowser.walk(path)

   List files and subdirectories recursively.
   
   :param path: directory path
   :type path: str

.. code:: python
   
   file_browser.walk('My Files')
   
Download
========
   
.. py:method:: FileBrowser.download(path)

   :param name: file path
   :type path: str

   Download a file.
   
.. code:: python
   
   file_browser.download('My Files/Documents/Sample.docx')
   
Create Directory
================
   
.. py:method:: FileBrowser.mkdir(path[, recurse = False])

   Create a directory.
   
   :param recurse: no error if existing, make parent directories as needed
   :type recurse: bool

.. code:: python
   
   file_browser.mkdir('My Files/Documents')
   
   file_browser.mkdir('The/quick/brown/fox', recurse = True)
   
Rename
======
   
.. py:method:: FileBrowser.rename(path, name)

   Rename a file or a folder.
   
   :param path: file path
   :param name: new file name
   :type path: str
   :type name: str
   
.. code:: python
   
   file_browser.rename('My Files/Documents/Sample.docx', 'Wizard Of Oz.docx')
   
Delete
======

.. py:method:: FileBrowser.delete(path)

   Delete a file or a folder.
   
   :param name: file or a folder path
   :type name: str
   
.. code:: python
   
   file_browser.delete('My Files/Documents/Sample.docx')
   
.. py:method:: FileBrowser.delete_multi(items...)

   Delete multiple files and folders.
   
   :param items: a comma separated list of file or folder paths
   :type items: str
   
.. code:: python
   
   file_browser.delete_multi('My Files/Documents/Sample.docx', 'The/quick/brown/fox')
   
Recover
=======
   
.. py:method:: FileBrowser.undelete(path)

   Recover a file or a folder.
   
   :param name: file or a folder path
   :type path: str
   
.. code:: python
   
   file_browser.undelete('My Files/Documents/Sample.docx')
   
.. py:method:: FileBrowser.undelete_multi(items...)

   Recover multiple files and folders.
   
   :param items: a comma separated list of file or folder paths
   :type items: str
   
.. code:: python
   
   file_browser.undelete_multi('My Files/Documents/Sample.docx', 'The/quick/brown/fox')
   
Copy
====
   
.. py:method:: FileBrowser.copy(src, dest)

   Copy a file or a folder.
   
   :param src: file or a folder path
   :param dest: destination folder path
   :type src: str
   :type dest: str
   
.. code:: python
   
   file_browser.copy('My Files/Documents/Sample.docx', 'The/quick/brown/fox')
   
.. py:method:: FileBrowser.copy_multi(src, dest)

   Copy multiple files and folders.
   
   :param src: list of file or folder paths
   :param dest: destination folder path
   :type src: list[str]
   :type dest: str
   
.. code:: python
   
   file_browser.copy_multi(['My Files/Documents/Sample.docx', 'My Files/Documents/Burndown.xlsx'], 'The/quick/brown/fox')
   
Move
====
   
.. py:method:: FileBrowser.move(src, dest)

   Move a file or a folder.
   
   :param src: file or a folder path
   :param dest: destination folder path
   :type src: str
   :type dest: str
   
.. code:: python
   
   file_browser.move('My Files/Documents/Sample.docx', 'The/quick/brown/fox')
   
.. py:method:: FileBrowser.move_multi(src, dest)

   Move multiple files and folders.
   
   :param src: list of file or folder paths
   :param dest: destination folder path
   :type src: list[str]
   :type dest: str
   
.. code:: python
   
   file_browser.move_multi(['My Files/Documents/Sample.docx', 'My Files/Documents/Burndown.xlsx'], 'The/quick/brown/fox')
   
Create Public Link
==================
   
.. py:method:: FileBrowser.mklink(path[, access = 'RO'][, expire_in = 30])

   Create a public link to a file or a folder.
   
   :param path: file or folder path
   :param access: file access permission
   :param expire_in: the validity period of the public link in days
   :type path: str
   :type access: str
   :type expire_in: int

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