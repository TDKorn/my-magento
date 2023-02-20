..  Title: MyMagento
..  Description: A Python package that wraps and extends the Magento 2 REST API
..  Author: TDKorn

.. |Tip| replace:: 💡 **Tip**
.. |RTD| replace:: **Explore the docs »**
.. _RTD: https://my-magento.readthedocs.io/en/latest/
.. |api_endpoint| replace:: API endpoint
.. _api_endpoint: https://adobe-commerce.redoc.ly/2.3.7-admin/
.. |.Client| replace:: Client
.. _.Client: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L13-L378
.. |.Model| replace:: Model
.. _.Model: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/model.py#L13-L241
.. |.SearchQuery| replace:: SearchQuery
.. _.SearchQuery: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L14-L313
.. |.execute| replace:: execute()
.. _.execute: https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L130-L141
.. |.ACCESS_TOKEN| replace:: ACCESS_TOKEN
.. _.ACCESS_TOKEN: https://github.com/TDKorn/my-magento/blob/v2.1.0/magento/clients.py#L72
.. |.USER_CREDENTIALS| replace:: USER_CREDENTIALS
.. _.USER_CREDENTIALS: https://github.com/TDKorn/my-magento/blob/v2.1.0/magento/clients.py#L67-L70


MyMagento🛒
---------------

.. image:: https://i.imgur.com/dkCWWYn.png
   :alt: Magento Logo
   :align: center
   :width: 200
   :height: 175

A Python package that wraps and extends the Magento 2 REST API

|RTD|_

|

.. image:: https://img.shields.io/pypi/v/my-magento?color=eb5202
   :target: https://pypi.org/project/my-magento/
   :alt: PyPI Version

.. image:: https://img.shields.io/badge/GitHub-my--magento-4f1abc
   :target: https://github.com/tdkorn/my-magento
   :alt: GitHub Repository

.. image:: https://static.pepy.tech/personalized-badge/my-magento?period=total&units=none&left_color=grey&right_color=blue&left_text=Downloads
    :target: https://pepy.tech/project/my-magento

.. image:: https://readthedocs.org/projects/my-magento/badge/?version=latest
    :target: https://my-magento.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

|

About MyMagento
~~~~~~~~~~~~~~~~~~~~

.. |note| replace:: 📝

+-------------------------------------------------------------+
| |note| What's MyMagento?                                    |
+=============================================================+
|  ``MyMagento`` is a highly interconnected package that      |
|  wraps and extends the Magento 2 REST API, providing a more |
|  intuitive and user-friendly interface to access and update |
|  your store                                                 |
+-------------------------------------------------------------+


MyMagento simplifies interaction with the Magento 2 REST API
=================================================================

If you've worked with the Magento 2 API, you'll know that not all endpoints are created equally.

``MyMagento`` aims to streamline your workflow by simplifying a
variety of commonly needed API operations.


Main Components
==================================

.. |comp| replace:: 💻
.. |mag| replace:: 🔍

+-------------------------------------------------------------+
| |comp| The |.Client|_                                       |
+=============================================================+
|  * Handles all API interactions                             |
|  * Supports multiple store views                            |
|  * Provides access to all other package components          |
+-------------------------------------------------------------+

+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+
| |mag| The |.SearchQuery|_ and Subclasses                                                                                                                        |
+=================================================================================================================================================================+
|  * |.execute|_ a predefined or custom search query on any endpoint                                                                                              |
|  * Simplified creation of basic and advanced `searches using REST endpoints <https://developer.adobe.com/commerce/webapi/rest/use-rest/performing-searches/>`_  |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------+
| 🧠 The |.Model|_ Subclasses                                                |
+============================================================================+
| * Wrap all API responses in the package                                    |
| * Provide additional endpoint-specific methods to retrieve and update data |
+----------------------------------------------------------------------------+


Available Endpoints
======================

``MyMagento`` is compatible with every |api_endpoint|_

Endpoints are wrapped with a `Model <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/model.py#L13-L241>`_ and `SearchQuery <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L14-L313>`_ subclass as follows:

+--------------------------+-------------------------------------+----------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------+
| **Endpoint**             | **Client Shortcut**                 |`SearchQuery <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L14-L313>`_ **Subclass** |`Model <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/model.py#L13-L241>`_ **Subclass**   |
+==========================+=====================================+==========================================================================================================+============================================================================================================+
| ``orders``               | ``Client.orders``                   | `OrderSearch <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L316-L411>`_            | `Order <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/order.py#L12-L182>`_               |
+--------------------------+-------------------------------------+----------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------+
| ``orders/items``         | ``Client.order_items``              | `OrderItemSearch <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L414-L526>`_        | `OrderItem <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/order.py#L185-L292>`_          |
+--------------------------+-------------------------------------+----------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------+
| ``invoices``             | ``Client.invoices``                 | `InvoiceSearch <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L529-L654>`_          | `Invoice <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/invoice.py#L11-L57>`_            |
+--------------------------+-------------------------------------+----------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------+
| ``products``             | ``Client.products``                 | `ProductSearch <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L657-L744>`_          | `Product <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/product.py#L12-L388>`_           |
+--------------------------+-------------------------------------+----------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------+
| ``products/attributes``  | ``Client.product_attributes``       | `ProductAttributeSearch <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L747-L775>`_ | `ProductAttribute <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/product.py#L559-L588>`_ |
+--------------------------+-------------------------------------+----------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------+
| ``categories``           | ``Client.categories``               | `CategorySearch <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L778-L820>`_         | `Category <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/category.py#L12-L146>`_         |
+--------------------------+-------------------------------------+----------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------+
| ``endpoint``             | ``Client.search("endpoint")``       | `SearchQuery <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/search.py#L14-L313>`_             | `APIResponse <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/models/model.py#L244-L286>`_        |
+--------------------------+-------------------------------------+----------------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------+

...

⚙ Installing MyMagento
~~~~~~~~~~~~~~~~~~~~~~~~~~

To install using ``pip``::

   pip install my-magento

Please note that ``MyMagento`` requires ``Python >= 3.10``


📚 Documentation
~~~~~~~~~~~~~~~~~~

Full documentation can be found on `ReadTheDocs <https://my-magento.readthedocs.io/en/latest/>`_


...

QuickStart: Login with MyMagento
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``MyMagento`` uses the `Client <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L13-L378>`_ class to handle all interactions with the API

.. _login: https://my-magento.readthedocs.io/en/latest/examples/logging-in.html
.. |login| replace:: Get a Magento 2 REST API Token With ``MyMagento``


+-------------------------------------------------------------+
| |Tip|                                                       |
+=============================================================+
| See |login|_ for full details on generating an access token |
+-------------------------------------------------------------+


Setting the Login Credentials
===================================

To generate an |.ACCESS_TOKEN|_ you'll need to `authenticate() <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L227-L254>`_ your |.USER_CREDENTIALS|_

Creating a `Client <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L13-L378>`_ requires a ``domain``, ``username``, and ``password`` at minimum.


.. code-block:: python

   >>> domain = 'website.com'
   >>> username ='username'
   >>> password = 'password'


If you're using a local installation of Magento you'll need to set ``local=True``. Your domain should look like this:

.. code-block:: python

   >>> domain = '127.0.0.1/path/to/magento'


...

Getting a `Client <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L13-L378>`_
=========================================================================================================

Option 1: Initialize a `Client <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L13-L378>`_ Directly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

      from magento import Client

      >>> api = Client(domain, username, password, **kwargs)


Option 2: Call `get_api <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/__init__.py#L16-L39>`_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python


      import magento

      >>> api = magento.get_api(**kwargs)

`get_api <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/__init__.py#L16-L39>`_ takes the same keyword arguments as the `Client <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L13-L378>`_, but if the ``domain``, ``username``, or ``password``
are missing, it will attempt to use the following environment variables:


.. code-block:: python

   import os

   os.environ['MAGENTO_DOMAIN'] = domain
   os.environ['MAGENTO_USERNAME']= username
   os.environ['MAGENTO_PASSWORD']= password

...

Getting an |.ACCESS_TOKEN|_
=======================================

Unless you specify ``login=False``, the `Client <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L13-L378>`_ will automatically call `authenticate() <https://github.com/tdkorn/my-magento/blob/v2.1.0/magento/clients.py#L227-L254>`_ once initialized


.. code-block:: python

   >>> api.authenticate()

   |[ MyMagento | website_username ]|:  Authenticating username on website.com...
   |[ MyMagento | website_username ]|:  Logged in to username


|

