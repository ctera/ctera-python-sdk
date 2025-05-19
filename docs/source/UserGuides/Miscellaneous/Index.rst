=============
Miscellaneous
=============

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
