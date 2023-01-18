.. _interact_with_api:

Interacting with the API
----------------------------

Performing a :meth:`~.search`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. |api_endpoints| replace:: API endpoint
.. _api_endpoints: https://adobe-commerce.redoc.ly/2.3.7-admin/

Using the :meth:`~.search` method, you can query any |api_endpoints|_ for data about
an individual or list of items:


.. admonition:: From the Docs…
   :class: docs

   .. automethod:: magento.clients.Client.search
      :noindex:


The following :class:`~.Client` attributes correspond to endpoint-specific :class:`~.SearchQuery` objects:

.. _client_search_attrs:

+----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| :attr:`.Client.orders`                                                     | Initializes an :class:`~.OrderSearch` for the ``orders`` endpoint                                                                                                                        |
+----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| :attr:`.Client.order_items`                                                | Initializes an :class:`~.OrderItemSearch` for the ``orders/items`` endpoint                                                                                                              |
+----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| :attr:`.Client.invoices`                                                   | Initializes an :class:`~.InvoiceSearch` for the ``invoices`` endpoint                                                                                                                    |
+----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| :attr:`.Client.products`                                                   | Initializes a :class:`~.ProductSearch` for the ``products`` endpoint                                                                                                                     |
+----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| :attr:`.Client.product_attributes`                                         | Initializes a :class:`~.ProductAttributeSearch` for the ``products/attributes`` endpoint                                                                                                 |
+----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| :attr:`.Client.categories`                                                 | Initializes a :class:`~.CategorySearch` for the ``categories`` endpoint                                                                                                                  |
+----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

...

.. admonition:: Example: :meth:`~.search` an endpoint
   :class: example

   .. code-block:: python

    # Query the "orders" endpoint
    >>> api.search("orders")  # api.orders
    <magento.search.OrderSearch object at 0x000001EB74FF4DC0>

    # Query an endpoint without a predefined SearchQuery
    >>> api.search("customers/addresses")
    <magento.search.SearchQuery object at 0x000001EB75482F20>

   For endpoints with no :class:`~.SearchQuery` and :class:`~.Model` defined,
   the :class:`~.APIResponse` is used as the wrapper class:

   .. code-block:: python

    # APIResponse wraps the result when the endpoint has no Model
    >>> address = api.search("customers/addresses").by_id(1)
    >>> print(address)
    <magento.models.model.APIResponse object at 0x00000260A5F2B340>

    >>> print(address.region)
    {'region_code': 'MI', 'region': 'Michigan', 'region_id': 33}


...

Search Results as Models
~~~~~~~~~~~~~~~~~~~~~~~~~

The :attr:`~.SearchQuery.result` data of any query is parsed and wrapped by the endpoint's
corresponding :class:`~.Model`, making it easier to interact with

.. code-block:: python

   # Retrieve product by sku
   >>> product = api.products.by_sku("24-MB01")
   >>> print(product)
   <Magento Product: 24-MB01>

   >>> print(f'Name: {product.name} | Price: {product.price}')
   Name: Joust Duffle Bag | Price: 99

   >>> product.categories
   [<Magento Category: Gear>, <Magento Category: Bags>]

   >>> product.media_gallery_entries
   [<MediaEntry 3417 for <Magento Product: 24-MB01>: Front View>, <MediaEntry 1 for <Magento Product: 24-MB01>: Side View>, ...]


Model Methods
===============

The Model classes have methods to update their data on the store, as well as to search for related items

.. admonition:: Example: Retrieving every :class:`~.Order` containing a :class:`~.Product`
   :class: example

   Using the same ``product`` from above, we can search for orders as follows

   .. code-block:: python

    # Using the Product itself
    >>> product.get_orders()

    [<Magento Order: "#000000003" placed on 2022-12-21 08:09:33>, ... ]

    # Using an OrderSearch
    >>> api.orders.by_product(product)
    >>> api.orders.by_product_id(product.id)
    >>> api.orders.by_sku(product.sku)

    [<Magento Order: "#000000003" placed on 2022-12-21 08:09:33>, ... ]



.. admonition:: Example: Retrieving a :class:`~.Category` and related ``Models``
   :class: example

   .. code-block:: python

    # Get Category data
    >>> category = api.categories.by_name("Watches")
    >>> category.get_products()
    [<Magento Product: 24-MG04>, <Magento Product: 24-MG01>, <Magento Product: 24-MG03>, ... ]

    >>> category.get_invoices()
    [<Magento Invoice: "#000000004"> for <Magento Order: "#000000004" placed on 2022-11-14 03:27:33>, ... ]


The :class:`~.Model` subclasses also have various methods to update data on the store, with scoping taken into account

.. code-block:: python

   # Update Product Stock
   >>> product.update_stock(3)
   |[ MyMagento | website_username ]|:  Updated stock to 4 for <Magento Product: 24-MB01>

   # Update thumbnail label on specific store view
   >>> product.thumbnail.set_alt_text('Thumbnail on "EN" store view', scope='EN')
   >>> print(product.thumbnail)
   <MediaEntry 3417 for <Magento Product: 24-MB01>: Thumbnail on "EN" store view>

...

Building Custom Search Queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to the predefined methods, you can build your own queries too – simply
:meth:`~.add_criteria`, :meth:`~.restrict_fields`, and :meth:`~.execute` the search


.. admonition:: Example
   :class: example

   .. code-block:: python

    # Retrieve orders placed since the start of 2023
    >>> api.orders.add_criteria(
    ...    field="created_at",
    ...    value="2023-01-01",
    ...    condition="gteq"
    ... ).execute()

    [<Magento Order: "#000000012" placed on 2023-01-02 05:19:55>, <Magento Order: "#000000013" placed on 2023-01-05 09:24:13>]


...

Making Raw Requests
~~~~~~~~~~~~~~~~~~~~

The :class:`~.Client` can also be used to generate the :meth:`~.url_for` any API endpoint,
including a store :attr:`~.scope`

.. code-block:: python

 # Generate the url for credit memo with id 7
 >>> api.url_for('creditmemo/7')
 "https://website.com/rest/V1/creditmemo/7"

 # Generate the same url on the "en" store view
 >>> api.url_for('creditmemo/7', scope='en')
 "https://domain.com/rest/en/V1/creditmemo/7"

An authorized :meth:`~.get`, :meth:`~.post`, :meth:`~.put`, or :meth:`~.delete` request can be made
to any endpoint url

.. code-block:: python

 >>> response = api.get(api.url_for('creditmemo/7'))
 >>> print(response.json())

 {'adjustment': 1.5, 'adjustment_negative': 0, 'adjustment_positive': 1.5, 'base_adjustment': 1.5,  ... }

