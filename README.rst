Paloma -- class based e-mails for Django
========================================

.. image:: https://travis-ci.org/iconfinder/paloma.png?branch=master
        :target: https://travis-ci.org/iconfinder/paloma

Inspired by Django's recent push towards using class based views to increase code reusability, Paloma provides a similar interface to working with e-mails.


Installation
------------

To install Paloma, do yourself a favor and don't use anything other than `pip <http://www.pip-installer.org/>`_:

.. code-block:: bash

    $ pip install django_paloma

Once installed, you also need to add Paloma to your list of ``INSTALLED_APPS`` in your application configuration:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'paloma',
    )
