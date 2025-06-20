Auditing
========

The SDK includes a module for recording all HTTP requests and exporting them as a Postman collection.
For more information, see:
`Import data into Postman <https://learning.postman.com/docs/getting-started/importing-and-exporting/importing-data/>`_
By default, auditing is disabled for performance reasons. If you need to enable Postman auditing, use the following commands:


.. code-block:: python

   import cterasdk.settings
   cterasdk.settings.audit.enabled = True
   cterasdk.settings.audit.filename = 'name-of-your-postman-collection-file'

   admin = GlobalAdmin('tenant.ctera.com')

.. note:: The Postman collection file is stored in your default Downloads directory.
