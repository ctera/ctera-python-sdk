************
File Browser
************

.. contents:: Table of Contents

List
====

.. automethod:: cterasdk.core.files.browser.FileBrowser.ls
   :noindex:

.. code:: python

   file_browser.ls('')  # List the contents of the Cloud Drive

   file_browser.ls('My Files')  # List the contents of the 'My Files' folder

   flie_browser.ls('My Files', True)  # Include both deleted and non-deleted files

   flie_browser.ls('My Files', True, True)  # Filter only deleted files

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

Collaboration Shares
====================

.. automethod:: cterasdk.core.files.browser.FileBrowser.share
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

.. automethod:: cterasdk.core.files.browser.FileBrowser.add_share_recipients
   :noindex:

.. note:: if the share recipients provided as an argument already exist, they will be skipped and not updated

.. automethod:: cterasdk.core.files.browser.FileBrowser.remove_share_recipients
   :noindex:

..

.. automethod:: cterasdk.core.files.browser.FileBrowser.unshare
   :noindex:

.. code:: python

   """
   Unshare a file or a folder
   """
   file_browser.unshare('Codebase')
   file_browser.unshare('My Files/Projects/2020/ProjectX')
   file_browser.unshare('Cloud/Albany')
