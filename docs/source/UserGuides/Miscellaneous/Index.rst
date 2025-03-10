=============
Miscellaneous
=============

Logging
=======

This library features numerous console loggers, with an option to redirect the output to a file.

    +--------------------------------+---------+--------------------------------------+
    |Logger name                     |Level    |Description                           |
    +================================+=========+======================================+
    |cterasdk                        |NOTSET   |Package Logger                        |
    +--------------------------------+---------+--------------------------------------+
    |cterasdk.edge                   |INFO     |Logger for CTERA Edge and Drive App   |
    +--------------------------------+---------+--------------------------------------+
    |cterasdk.core                   |INFO     |Logger for CTERA Portal               |
    +--------------------------------+---------+--------------------------------------+
    |cterasdk.common                 |INFO     |Common Infrastructure Logger          |
    +--------------------------------+---------+--------------------------------------+
    |cterasdk.metadata.connector     |INFO     |Notification Service Logger           |
    +--------------------------------+---------+--------------------------------------+
    |cterasdk.http                   |ERROR    |Transport Layer Logger                |
    +--------------------------------+---------+--------------------------------------+
    |cterasdk.http.trace             |ERROR    |Transport Layer Tracing               |
    +--------------------------------+---------+--------------------------------------+
    |cterasdk.crypto                 |ERROR    |Cryptography Logger                   |
    +--------------------------------+---------+--------------------------------------+
    |cterasdk.filesystem             |ERROR    |Local File System Logger              |
    +--------------------------------+---------+--------------------------------------+

List the available loggers:

.. code:: python

   import logging
   import cterasdk.logging

   print({name: logging.getLevelName(logging.getLogger(name).level) for name in logging.root.manager.loggerDict})

To update the log level of a logger:

.. code:: python

   import logging
   import cterasdk.logging

   logging.getLogger('cterasdk.metadata.connector').setLevel(logging.DEBUG)  # Enables 'DEBUG'

Redirecting log output to a file:

.. code:: console

   set cterasdk.log=cterasdk.log  # Redirect output to 'cterasdk.log' in the current directory

   set cterasdk.log=C:/users/username/Desktop/cterasdk.log  # Redirect output to an alternate location

.. code:: bash

   export cterasdk.log="cterasdk.log"

   export cterasdk.log="/home/username/cterasdk.log"


Auditing
========

The SDK includes a module for recording all HTTP requests and exporting them as a Postman collection.
For more information, see:
`Import data into Postman <https://learning.postman.com/docs/getting-started/importing-and-exporting/importing-data/>`_ 
By default, auditing is disabled for performance reasons. If you need to enable Postman auditing, use the following commands:


.. code-block:: python

   import cterasdk.settings
   cterasdk.settings.sessions.management.audit.postman.enabled = True
   cterasdk.settings.sessions.management.audit.postman.name = 'name-of-your-postman-collection-file'

   admin = GlobalAdmin('tenant.ctera.com')

.. note:: The Postman collection file is stored in your default Downloads directory.


Serialization
=============

This library features JSON and XML serialization, in alignment with the CTERA API schema.

.. autofunction:: cterasdk.convert.serializers.toxmlstr
   :noindex:

.. code-block:: python

   user = Object()
   user.name = 'alice'
   user.firstName = 'Alice'
   user.lastName = 'Wonderland'
   user.email = 'alice@adventures.com'
   user.password = 'Passw0rd1!'
   print(toxmlstr(user))
   print(toxmlstr(user, True))

.. autofunction:: cterasdk.convert.serializers.tojsonstr
   :noindex:

.. code-block:: python

   user = Object()
   user.name = 'alice'
   user.firstName = 'Alice'
   user.lastName = 'Wonderland'
   user.email = 'alice@adventures.com'
   user.password = 'Passw0rd1!'
   print(tojsonstr(user))
   {
        "lastName": "Wonderland",
        "password": "Passw0rd1!",
        "name": "alice",
        "firstName": "Alice",
        "email": "alice@adventures.com"
   }
   print(tojsonstr(user, False))
   {"lastName": "Wonderland", "password": "Passw0rd1!", "name": "alice", "firstName": "Alice", "email": "alice@adventures.com"}
