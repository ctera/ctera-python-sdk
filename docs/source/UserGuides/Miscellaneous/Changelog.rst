Changelog
=========

2.20.20
-------

Improvements
^^^^^^^^^^^^

* Added a unique ``User-Agent`` header to all requests made by the CTERA Python SDK
* Raised exceptions on upload errors to CTERA Portal
* Raised :py:class:`cterasdk.exceptions.session.SessionExpired` upon session expiration
* Listed the Cloud Drive root by default if no ``path`` argument was
  provided to :py:func:`cterasdk.core.files.browser.FileBrowser.listdir`
* Added :py:class:`cterasdk.exceptions.notifications.AncestorsError` exception
* Added :py:class:`cterasdk.exceptions.transport.TLSError` exception
* Suppressed session expiration exceptions on logout
* Added support for resolving file conflicts on copy and move
  operations using :py:class:`cterasdk.core.types.ConflictResolver`

Bug Fixes
^^^^^^^^^

* Corrected Direct I/O object class references in the documentation

.. code:: python

   """Catching upload exceptions"""
   try:
       ...
   except cterasdk.exceptions.io.OutOfQuota as e:
       print('Failure due to quota violation.')
   except cterasdk.exceptions.io.RejectedByPolicy as e:
       print('Failure due to Cloud Drive policy violation.')
   except cterasdk.exceptions.io.NoStorageBucket as e:
       print('No backend storage bucket is available.')
   except cterasdk.exceptions.io.WindowsACLError as e:
       print('Attempt to upload a file to a Windows ACL-enabled cloud drive folder.')
   except cterasdk.exceptions.io.UploadException:
       print('Base exception for any upload errors.')

   """Catching expired sessions"""
   try:
       ...
   except cterasdk.exceptions.session.SessionExpired as e:
       print('Session expired. Re-authenticate to establish a new session.')

* Starting with this version, the CTERA Python SDK ``User-Agent`` header is formatted as follows:

.. code::

   CTERA Python SDK/2.20.20; aiohttp/3.9.5; (Windows 10; AMD64; Python 3.11.4);

* Introduced support for resolving conflicts during copy and move operations

.. code:: python

   """Override destination on conflict"""
   resolver = core_types.ConflictResolver.override()
   user.files.copy(('My Files/Gelato.pptx', 'My Files/Slides/Gelato.pptx'), resolver=resolver)

   """Resume job from cursor"""
   objects = (
       'My Files/Gelato.pptx', 'My Files/Slides/Gelato.pptx',
       'Spreadsheets/Q1Summary.xlsx', 'Sheets/Q1Summary.pptx'
   )
   try:
       user.files.copy(objects)
   except cterasdk.exceptions.io.FileConflict as e:
       resolver = core_types.ConflictResolver.override()  # override destination
       user.files.copy(objects, resolver=resolver, cursor=e.cursor)  # resume copy from cursor

Related issues and pull requests on GitHub: `#316 <https://github.com/ctera/ctera-python-sdk/pull/316>`_,
`#317 <https://github.com/ctera/ctera-python-sdk/pull/317>`_
`#318 <https://github.com/ctera/ctera-python-sdk/pull/318>`_

2.20.19
-------

Improvements
^^^^^^^^^^^^

* Refactored the CTERA Direct I/O module to reduce duplicate code and improve exception handling.
* Added support for configuring Cloud Drive folders with Global File Locking.
* Improved authentication error handling by catching HTTP exceptions and raising :py:class:`cterasdk.exceptions.auth.AuthenticationError`.
* Added an attribute to indicate whether deduplication is enabled when retrieving the deduplication status.
* Raise an exception when uploading a file with invalid characters in its name.
* Raise an exception when attempting to upload files to the Cloud Drive root directory.
* Added support for exporting data discovery and migration jobs to CSV format.
* Introduced an asynchronous task management module for operations such as copying, moving, renaming, deleting, or undeleting files.
* Background tasks now return awaitable objects: :py:class:`cterasdk.lib.tasks.AwaitableEdgeTask`,
  :py:class:`cterasdk.lib.tasks.AwaitablePortalTask`.

Bug Fixes
^^^^^^^^^

* Fixed an `AttributeError` when a connection error occurs while waiting for an Edge Filer to reboot.

Related issues and pull requests on GitHub: `#315 <https://github.com/ctera/ctera-python-sdk/pull/315>`_

.. code:: python

  # Background task: 'Apply Provisioning Changes'
  result = admin.users.apply_changes(wait=True)  # Wait for provisioning changes to complete and return the result

  awaitable_task = admin.users.apply_changes()  # Return an awaitable task object without waiting
  result = awaitable_task.status()              # Get the current status of the task
  result = awaitable_task.wait()                # Wait for task completion
  result = awaitable_task.wait(timeout=5)       # Wait up to 5 seconds for the task to complete

  # Moving files and folders
  result = user.files.move(('My Files/doc.docx', 'Documents/Guide.docx'))  # Move a file and wait for completion

  awaitable_task = user.files.move(('My Files/doc.docx', 'Documents/Guide.docx'), wait=False)  # Return an awaitable task object
  result = awaitable_task.wait()  # Wait for the move operation to complete

..

2.20.18
-------

Improvements
^^^^^^^^^^^^

* Added support for managing email alerts on Edge Filers.

Bug Fixes
^^^^^^^^^

* Fixed an issue where email server credentials were not stored correctly due to a missing class name in the object.

Related issues and pull requests on GitHub: `#314 <https://github.com/ctera/ctera-python-sdk/pull/314>`_

2.20.17
-------

Improvements
^^^^^^^^^^^^

* Added support to validate if deduplication is enabled on the CTERA Edge Filer

Related issues and pull requests on GitHub: `#313 <https://github.com/ctera/ctera-python-sdk/pull/313>`_,

2.20.16
-------

Improvements
^^^^^^^^^^^^

* Added support for enabling or disabling Direct Mode on CTERA Portal Storage Nodes.
* Support copying and moving multiple sources to multiple destinations on CTERA Portal.

Bug Fixes
^^^^^^^^^

* Removed redundant call when retrieving the list of domain mappings.

Related issues and pull requests on GitHub: `#310 <https://github.com/ctera/ctera-python-sdk/pull/310>`_,
`#311 <https://github.com/ctera/ctera-python-sdk/pull/311>`_
`#312 <https://github.com/ctera/ctera-python-sdk/pull/312>`_

.. code:: python

  """
  Copy multiple sources: the 'Sample.docx' file and the 'Spreadsheets' directory to 'My Files/Archive'
  """
  user.files.copy('My Files/Documents/Sample.docx', 'My Files/Spreadsheets', destination='My Files/Archive')

  """
  Copy multiple sources to different destinations under a different name.
  """
  user.files.copy(
    ("Docs/Report_January.docx", "Archive/Jan_Report_Final.docx"),
    ("Budget/Budget_2024.xlsx", "Finance/2024_Annual_Budget.xlsx"),
    ("Presentations/Presentation.pptx", "Sales/Q2_Sales_Pitch.pptx")
  )

2.20.15
-------

Improvements
^^^^^^^^^^^^

* Support retrieving, adding, and removing Edge Filer hosts file entries.
* Add documentation for the Edge Filer Ransomware Protection APIs.
* Add support for managing the Edge Filer's Antivirus (Bit Defender).

Bug Fixes
^^^^^^^^^

* Fixed a documentation error related to deleting and undeleting Team Portal tenants.
* Fixed an error when printing Edge Filer throttling policy rules set to "Every Day".

Related issues and pull requests on GitHub: `#306 <https://github.com/ctera/ctera-python-sdk/pull/306>`_,
`#307 <https://github.com/ctera/ctera-python-sdk/pull/307>`_,
`#308 <https://github.com/ctera/ctera-python-sdk/pull/308>`_,
`#309 <https://github.com/ctera/ctera-python-sdk/pull/309>`_


2.20.14
-------

Bug Fixes
^^^^^^^^^

* CTERA Portal: Added support for special characters when copying, moving, renaming, sharing, and deleting files.

Related issues and pull requests on GitHub: `#305 <https://github.com/ctera/ctera-python-sdk/pull/305>`_

2.20.13
-------

Bug Fixes
^^^^^^^^^

* Increased the HTTP request timeout when long polling for changes.
* Updated the default socket connection and read timeouts for synchronous Edge Filer access to 30 and 60 seconds, respectively.

Related issues and pull requests on GitHub: `#303 <https://github.com/ctera/ctera-python-sdk/pull/303>`_


2.20.12
-------

Improvements
^^^^^^^^^^^^

* Support for overriding timeout settings on a per-request basis.
* Increased the ``sock_read`` timeout to 2 minutes when invoking :py:func:`cterasdk.edge.network.Network.tcp_connect`.

Related issues and pull requests on GitHub: `#302 <https://github.com/ctera/ctera-python-sdk/pull/302>`_


2.20.11
-------

Improvements
^^^^^^^^^^^^

* Added a compatibility notice.
* Included the changelog in the CTERA Python SDK documentation.

*Related issues and pull requests on GitHub:* `#301 <https://github.com/ctera/ctera-python-sdk/pull/301>`_

2.20.10
-------

Improvements
^^^^^^^^^^^^

* Revamped the exception modules in ``cterasdk.exceptions``.
* Added support for file-walk operations without specifying a path (defaults to the root directory).
* Implemented automatic file rename during upload if the destination path includes a file name that already exists.

*Related issues and pull requests on GitHub:* `#300 <https://github.com/ctera/ctera-python-sdk/pull/300>`_

2.20.9
------

Improvements
^^^^^^^^^^^^

* Introduced new exceptions for HTTP errors.
* Added support for listing and walking directories via WebDAV on the Edge Filer using ``AsyncEdge`` and ``Edge`` clients.
* Added a method to check if a file or folder exists.

*Related issues and pull requests on GitHub:* `#299 <https://github.com/ctera/ctera-python-sdk/pull/299>`_


2.20.8
------

What's New
^^^^^^^^^^

* Added compatibility for CTERA Direct IO with CTERA Portal v8.3.

*Related issues and pull requests on GitHub:* `#298 <https://github.com/ctera/ctera-python-sdk/pull/298>`_


2.20.7
------

Improvements
^^^^^^^^^^^^

* Updated :py:class:`cterasdk.common.object.Object` to inherit from ``MutableMapping``, enabling dictionary-like access.
* Added support for the HTTP PROPFIND method.

*Related issues and pull requests on GitHub:* `#297 <https://github.com/ctera/ctera-python-sdk/pull/297>`_


2.20.6
------

Bug Fixes
^^^^^^^^^

* Added support for deleting multiple files on the Edge Filer in a single call.

*Related issues and pull requests on GitHub:* `#296 <https://github.com/ctera/ctera-python-sdk/pull/296>`_


2.20.5
------

Bug Fixes
^^^^^^^^^

* Fixed an issue where ``AsyncGlobalAdmin`` could not browse Team Portal tenants.


2.20.4
------

Bug Fixes
^^^^^^^^^

* Moved instantiation of the TCP connector to the point of ``ClientSession`` creation.

*Related issues and pull requests on GitHub:* `#295 <https://github.com/ctera/ctera-python-sdk/pull/295>`_


2.20.3
------

What's New
^^^^^^^^^^

* This version introduces a new ``AsyncEdge`` object for asynchronous access to the CTERA Edge Filer.
* Supported file browser operations include:
  ``listdir``, ``handle``, ``handle_many``, ``download``, ``download_many``,
  ``upload``, ``upload_file``, ``mkdir``, ``makedirs``, ``copy``, ``move``, and ``delete``.

Improvements
^^^^^^^^^^^^

* Logging is no longer enabled by default. As of this version, it is the responsibility of the
  client application to configure logging explicitly.
  This change aligns with best practices for libraries and allows greater flexibility in how logs are managed.

* Introduced improved configuration settings to support both synchronous and asynchronous access to the CTERA Portal and Edge Filers.

  .. code-block:: python

      # Disable TLS verification for CTERA Portal clients
      cterasdk.settings.core.syn.settings.connector.ssl = False  # GlobalAdmin, ServicesPortal
      cterasdk.settings.core.asyn.settings.connector.ssl = False  # AsyncGlobalAdmin, AsyncServicesPortal

      # Disable TLS verification for CTERA Edge Filer clients
      cterasdk.settings.edge.syn.settings.connector.ssl = False  # Edge
      cterasdk.settings.edge.asyn.settings.connector.ssl = False  # AsyncEdge

*Related issues and pull requests on GitHub:* `#294 <https://github.com/ctera/ctera-python-sdk/pull/294>`_

