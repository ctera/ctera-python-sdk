***************
Getting Started
***************

Importing the Library
---------------------

To import the `cterasdk` core library, use:

.. code:: python

   from cterasdk import *

Logging
-------

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
^^^^^^^^^^

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
