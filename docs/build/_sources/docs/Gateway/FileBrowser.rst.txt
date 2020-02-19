************
File Browser
************

.. contents:: Table of Contents

Obtaining Access to the Gateway's File System
---------------------------------------------

.. code:: python

   filer = Gateway('vGateway-0dbc')
   
   filer.login('USERNAME', 'PASSWORD')
   
   file_browser = filer.files() # returns a instance of FileBrowser class object
   
List
====

.. py:method:: FileBrowser.ls(path)

   List a directory.

   TODO
   
Download
========
   
.. py:method:: FileBrowser.download(path)

   Download a file.
   
.. code:: python
   
   file_browser.download('cloud/users/Service Account/My Files/Documents/Sample.docx')
   
Create Directory
================
   
.. py:method:: FileBrowser.mkdir(path[, recurse = False])

   Create a directory.
   
   :param recurse: no error if existing, make parent directories as needed
   :type recurse: bool

.. code:: python
   
   file_browser.mkdir('cloud/users/Service Account/My Files/Documents')
   
   file_browser.mkdir('cloud/users/Service Account/My Files/The/quick/brown/fox', recurse = True)
   
Delete
======
   
.. py:method:: FileBrowser.delete(path)

   Download a file or a folder.
   
.. code:: python
   
   file_browser.delete('cloud/users/Service Account/My Files/Documents')