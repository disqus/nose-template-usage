nose-template-usage
===================

A Nose plugin that displays which Django templates were and were not used
(loaded) during test execution.

Installation
------------

::

    pip install nose-template-usage

Usage
-----

To enable the template usage report, include the ``--with-template-usage-report``
command line option when running your tests with ``python setup.py nosetests``
or the ``nosetests`` command.

Ignoring Directories
~~~~~~~~~~~~~~~~~~~~

You probably don't want to include templates from third-party libraries in your
template usage report. To ignore template prefixes, use the
``--ignore-template-prefix=path/`` option. The value of the ``path/`` is the
path relative to the template loader.
