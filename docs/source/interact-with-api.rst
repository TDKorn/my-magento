.. _interact_with_api:

Interacting with the API
----------------------------

Did you :ref:`logging-in`? Then let's start using the API!


Performing a :meth:`~.search`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. |api_endpoints| replace:: API endpoint
.. _api_endpoints: https://adobe-commerce.redoc.ly/2.3.7-admin/


The :meth:`.Client.search` method lets you :meth:`~.execute` a query on
any |api_endpoints|_

It creates a :class:`~.SearchQuery` for the endpoint,
allowing you to retrieve data about

* An individual item (ex. :meth:`~.SearchQuery.by_id`)
* A list of items (ex. :meth:`~.SearchQuery.by_list`)
* Any search criteria you desire (see :ref:`Custom Queries`)


.. admonition:: From the Docs…
   :class: docs

   .. automethod:: magento.clients.Client.search
      :noindex:



.. rubric:: Example: :meth:`~.search` an endpoint :meth:`~.by_id`

.. code-block:: python

    # Query the "invoices" endpoint (also: api.invoices)
    >>> api.search("invoices").by_id(1)

    <Magento Invoice: "#000000001"> for <Magento Order: "#000000001" placed on 2022-11-01 03:27:33>



.. rubric:: Example: :meth:`~.search` an endpoint :meth:`~.by_list`

.. code-block::

    # Retrieve invoices from a list of invoice ids
    >>> ids = list(range(1,101))
    >>> api.invoices.by_list("entity_id", ids)

    [<Magento Invoice: "#000000001"> for <Magento Order: "#000000001" placed on 2022-11-01 03:27:33>, ...]

...

Search Results: The :class:`~.Model` Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. |the_models| replace:: the ``magento.models`` subpackage
.. _the_models: models.html

The :attr:`~.SearchQuery.result` of any :class:`~.SearchQuery` will be parsed and wrapped by a
:class:`~.Model` class in |the_models|_, making the API response data easier to work with.


These classes also provide endpoint-specific methods to search for related items and update store data.

.. rubric:: Example: Retrieving every :class:`~.Order` containing a :class:`~.Product`

Using the :class:`~.Product` from above, we can search for orders as follows

.. code-block::

    # Using the Product itself
    >>> product.get_orders()

    [<Magento Order: "#000000003" placed on 2022-12-21 08:09:33>, ... ]

    # Using an OrderSearch
    >>> api.orders.by_product(product)
    >>> api.orders.by_product_id(product.id)
    >>> api.orders.by_sku(product.sku)

    [<Magento Order: "#000000003" placed on 2022-12-21 08:09:33>, ... ]



.. rubric:: Example: Retrieving some items related to a :class:`~.Category`


.. code-block::

    # Get Category data
    >>> category = api.categories.by_name("Watches")
    >>> category.get_products()
    >>> category.get_invoices()

    [<Magento Product: 24-MG04>, <Magento Product: 24-MG01>, <Magento Product: 24-MG03>, ... ]
    [<Magento Invoice: "#000000004"> for <Magento Order: "#000000004" placed on 2022-11-14 03:27:33>, ... ]



.. rubric:: Example: Updating the Thumbnail :class:`~.MediaEntry` of a :class:`~.Product`

.. code-block::

    # Update product thumbnail label on specific store view

   >>> product.thumbnail.set_alt_text("bonjour", scope="FR")
   >>> print(product.thumbnail)

    <MediaEntry 3417 for <Magento Product: 24-MB01>: bonjour>

...


.. tip:: If you have multiple store views, a ``store_code`` can be specified when
   retrieving/updating data

   * The :attr:`.Client.scope` is used by default - simply change it to switch store :attr:`~.views`
   * Passing the ``scope`` keyword argument to :meth:`.Client.url_for`, :meth:`.Model.refresh`,
     and some Model update methods will temporarily override the Client scope

...



.. _Custom Queries:

Building Custom Search Queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to the predefined methods, you can also build your own queries – simply
:meth:`~.add_criteria`, :meth:`~.restrict_fields`, and :meth:`~.execute` the search

* The :meth:`~.since` and :meth:`~.until` methods allow you to further filter your query by date


.. admonition:: Example
   :class: example

   .. code-block::

    # Retrieve orders over $50 placed since the start of 2023
    >>> api.orders.add_criteria(
    ...    field="grand_total",
    ...    value="50",
    ...    condition="gt"
    ... ).since("2023-01-01").execute()

    [<Magento Order: "#000000012" placed on 2023-01-02 05:19:55>, <Magento Order: "#000000013" placed on 2023-01-05 09:24:13>]


...


Making Authorized Requests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :class:`~.Client` can be used to generate the :meth:`~.url_for` any API endpoint,
including a store :attr:`~.scope`.

You can use this URL to make an authorized
:meth:`~.get`, :meth:`~.post`, :meth:`~.put`, or :meth:`~.delete` request.


Example: Making a :meth:`~.get` Request
=============================================
.. code-block::

 # Request the data for credit memo with id 7
 >>> url = api.url_for('creditmemo/7')
 >>> response = api.get(url)
 >>> print(response.json())

 {'adjustment': 1.5, 'adjustment_negative': 0, 'adjustment_positive': 1.5, 'base_adjustment': 1.5,  ... }


.. note:: Many endpoints need to be wrapped still, but most :meth:`~.get` requests will still be
   simplified through a :meth:`~.search`

   .. code-block::

        # Retrieve credit memo with id 7 using a search
        >>> memo = api.search("creditmemo").by_id(7)
        >>> print(memo, memo.data, sep='\n')

        <magento.models.model.APIResponse object at 0x000001BA42FD0FD1>
        {'adjustment': 1.5, 'adjustment_negative': 0, 'adjustment_positive': 1.5, 'base_adjustment': 1.5,  ... }


Example: Making a :meth:`~.post` Request
=============================================

.. code-block::

    # Add a comment to credit memo with id 7
    >>> url = api.url_for("creditmemo/7/comments")
    >>> payload = {
            "entity": {
                "comment": "this is a comment",
                "is_customer_notified": 0,
                "is_visible_on_front": 0,
                "parent_id": 20
            }
        }
    >>> response = api.post(url, payload)


.. tip:: The :meth:`.Model.data_endpoint` will usually be
   close to the url to :meth:`~.post` to

   .. code-block::

        # The same as above, but using a search
        >>> memo = api.search("creditmemo").by_id(7)
        >>> url = memo.data_endpoint() + '/comments'
        >>> response = api.post(url, payload)
