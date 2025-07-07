Changelog
=========

2.20.16
-------

Improvements
^^^^^^^^^^^^

* Added support for enabling or disabling Direct Mode on CTERA Portal Storage Nodes.
* Introduced a method for setting the Advanced Domain Mapping configuration. **Note:** This method requires the full list of mappings to be provided and will overwrite the existing configuration.

Bug Fixes
^^^^^^^^^

* Removed redundant call when retrieving the list of domain mappings.

Related issues and pull requests on GitHub: `#310 <https://github.com/ctera/ctera-python-sdk/pull/310>`_,
`#311 <https://github.com/ctera/ctera-python-sdk/pull/311>`_

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

