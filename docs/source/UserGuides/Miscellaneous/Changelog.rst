Changelog
=========

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

