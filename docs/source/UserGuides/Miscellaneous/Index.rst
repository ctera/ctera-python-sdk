=============
Miscellaneous
=============


Exceptions
==========

.. autoclass:: cterasdk.exceptions.CTERAException
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.ObjectNotFoundException
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.InputError
   :noindex:
   :members:
   :show-inheritance:

Session
-------

.. autoclass:: cterasdk.exceptions.session.NotLoggedIn
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.session.SessionExpired
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.session.ContextError
   :noindex:
   :members:
   :show-inheritance:

I/O
---

.. autoclass:: cterasdk.exceptions.io.RemoteStorageException
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.io.ResourceNotFoundError
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.io.NotADirectory
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.io.ResourceExistsError
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.io.PathValidationError
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.io.NameSyntaxError
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.io.ReservedNameError
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.io.RestrictedPathError
   :noindex:
   :members:
   :show-inheritance:

Notification Service
--------------------

.. autoclass:: cterasdk.exceptions.notifications.NotificationError
   :noindex:
   :members:
   :show-inheritance:


HTTP Transport
--------------

.. autoclass:: cterasdk.exceptions.transport.HTTPError
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.transport.BadRequest
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.transport.Unauthorized
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.transport.Forbidden
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.transport.NotFound
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.transport.Unprocessable
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.transport.InternalServerError
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.transport.BadGateway
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.transport.ServiceUnavailable
   :noindex:
   :members:
   :show-inheritance:

.. autoclass:: cterasdk.exceptions.transport.GatewayTimeout
   :noindex:
   :members:
   :show-inheritance:

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
