.. |RTD| replace:: **Explore the docs »**
.. _RTD: https://my-magento.readthedocs.io/en/latest/

MyMagento
---------------

.. image:: _static/magento_orange.png
   :alt: Magento Logo
   :align: center
   :width: 100
   :height: 100

A Python package that wraps and extends the Magento 2 REST API

|RTD|_

|

.. image:: https://img.shields.io/pypi/v/my-magento?color=orange
   :target: https://pypi.org/project/my-magento/
   :alt: PyPI Version

.. image:: https://static.pepy.tech/personalized-badge/my-magento?period=total&units=none&left_color=grey&right_color=blue&left_text=Downloads
    :target: https://pepy.tech/project/my-magento

.. image:: https://readthedocs.org/projects/my-magento/badge/?version=latest
    :target: https://my-magento.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

|

About MyMagento
~~~~~~~~~~~~~~~~~~~~

.. admonition:: What's MyMagento?
   :class: note

   ``MyMagento`` is a highly interconnected package that wraps and extends the Magento 2 REST API,
   providing a more intuitive and user-friendly interface to access and update your store.

...

MyMagento simplifies interaction with the Magento 2 REST API
================================================================

If you've worked with the Magento 2 API, you'll know that not all endpoints are created equally.

``MyMagento`` aims to streamline your workflow, offering efficient API wrapper methods for a large number
of API operations across multiple endpoints. It takes care of the small details so that you can
stay focused on the more important aspects of managing your store.

...


Main Components
==================================

.. .. image:: https://user-images.githubusercontent.com/96394652/212470049-ebc2c46b-1fb1-44d1-a400-bf3cdfd3e4fb.png
   :alt: The Client
   :target: https://github.com/TDKorn/my-magento/blob/sphinx-docs/magento/clients.py

.. admonition:: The :class:`~.Client`
   :class: client

   * Handles all interactions with the API, with support for multiple store views
   * Accessible from all objects created by the package

.. admonition:: The :class:`~.SearchQuery` and Subclasses
   :class: search

   * :meth:`~.execute`  predefined or custom search queries on any endpoint
   * Supports simple and advanced `searches using REST endpoints <https://developer.adobe.com/commerce/webapi/rest/use-rest/performing-searches/>`_


.. admonition::  The :class:`~.Model` Subclasses
   :class: hint

   * Wrap all API responses in the package
   * Provide additional endpoint-specific functionality for data updates and retrieval

...

Installation
~~~~~~~~~~~~~~~~~~~

.. admonition:: Installing MyMagento
   :class: client

   To install using ``pip``::

    pip install my-magento

   Please note that ``MyMagento`` requires ``Python >= 3.10``


Documentation
~~~~~~~~~~~~~~

Full documentation can be found on `ReadTheDocs <my-magento.readthedocs.io/en/latest/>`_


...

QuickStart: Login with MyMagento
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the credentials of your Magento 2 admin account to initialize and :meth:`~.authenticate` a :class:`~.Client`

.. code-block:: python

 from magento import Client

 >>> api = Client('website.com','username', 'password', login=False)
 >>> api.authenticate()

 |[ MyMagento | website_username ]|:  Authenticating username on website.com...
 |[ MyMagento | website_username ]|:  Logged in to username


Once you initialize a ``Client``, you have a few ways to start `interacting with the api <https://my-magento.readthedocs.io/en/latest/interact-with-api.html#interact-with-api>`_

...

Interacting with the API
~~~~~~~~~~~~~~~~~~~~~~~~~~

For the rest of this README, please refer to the `docs <https://my-magento.readthedocs.io/en/latest/interact-with-api.html#interact-with-api>`_



