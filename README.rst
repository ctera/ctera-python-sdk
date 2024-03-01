====================
CTERA SDK for Python
====================

.. image:: https://travis-ci.com/ctera/ctera-python-sdk.svg?branch=master
   :target: https://travis-ci.com/ctera/ctera-python-sdk
.. image:: https://github.com/ctera/ctera-python-sdk/workflows/CI/badge.svg
   :target: https://github.com/ctera/ctera-python-sdk/actions?query=workflow%3ACI
.. image:: https://readthedocs.org/projects/ctera-python-sdk/badge/?version=latest
   :target: https://ctera-python-sdk.readthedocs.io/en/latest
   :alt: [Latest Release Documentation]
.. image:: https://snyk.io/test/github/ctera/ctera-python-sdk/badge.svg
   :target: https://snyk.io/test/github/ctera/ctera-python-sdk
.. image:: https://img.shields.io/pypi/v/cterasdk
   :target: https://pypi.org/pypi/cterasdk
   :alt: [Latest Release Version]
.. image:: https://img.shields.io/pypi/wheel/cterasdk
   :target: https://pypi.org/pypi/cterasdk
   :alt: PyPI - Wheel
.. image:: https://img.shields.io/pypi/l/cterasdk
   :target: https://opensource.org/licenses/Apache-2.0
   :alt: [Latest Release License]
.. image:: https://img.shields.io/pypi/pyversions/cterasdk
   :target: https://pypi.org/pypi/cterasdk
   :alt: [Latest Release Supported Python Versions]
.. image:: https://img.shields.io/pypi/status/cterasdk
   :target: https://pypi.org/pypi/cterasdk
   :alt: [Latest Release Development Stage]

The CTERA SDK for Python provides developers with powerful tools to automate the deployment and configuration 
of the CTERA Global File System, streamline data management tasks, 
and seamlessly integrate CTERA's global namespace with their applications.

Documentation
=============

User documentation is available on `Read the Docs <http://ctera-python-sdk.readthedocs.org/>`_.

Installation
============

Installing via `pip <https://pip.pypa.io/>`_:

.. code-block:: console

   $ pip install cterasdk

Install from source:

.. code-block:: console

   $ git clone https://github.com/ctera/ctera-python-sdk.git
   $ cd ctera-python-sdk
   $ python setup.py install

Importing the Library
======================

To get started, open a Python console:

.. code-block:: python
   
   from cterasdk import *

Building Documentation
======================

Documentation can be compiled by running ``make html`` from the ``docs``
folder. After compilation, open ``docs/build/html/index.html``.

Testing
=======

We use the `tox <https://tox.readthedocs.org/>`_ package to run tests in Python
3. To install, use :code:`pip install tox`. Once installed, run `tox` from the
root directory.

.. code-block:: console

   $ tox
