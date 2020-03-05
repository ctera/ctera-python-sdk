*************
Miscellaneous
*************
Logging
#######

The library includes a built-in console logger. The logger's configuration is controlled by the ``config.Logging.get()`` class object.

Disabling the Logger
====================

The logger is enabled by default. To disable the logger, run:

.. code:: python

   config.Logging.get().disable()

Changing the Log Level
======================

The default logging level is set to ``logging.INFO``. To change the log level, run:

.. code:: python

   config.Logging.get().setLevel(logging.ERROR) # will log severity >= error

   config.Logging.get().setLevel(logging.WARNING) # will log severity >= warning

Log Levels
----------

The available log levels are:

    +----------+-------------+
    |Level     |Numeric Value|
    +==========+=============+
    |CRITICAL  |50           |
    +----------+-------------+
    |ERROR     |40           |
    +----------+-------------+
    |WARNING   |30           |
    +----------+-------------+
    |INFO      |20           |
    +----------+-------------+
    |DEBUG     |10           |
    +----------+-------------+


Formatting
##########

The following formatting functions are included in this library:

.. autofunction:: cterasdk.convert.format.tojsonstr
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

.. autofunction:: cterasdk.convert.format.toxmlstr
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
