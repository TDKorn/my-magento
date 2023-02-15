Changelog
----------

v2.1.0
~~~~~~~

* Added :meth:`~.get_api` to login using credentials stored in environment variables

  - The environment variables ``MAGENTO_USERNAME``, ``MAGENTO_PASSWORD``, ``MAGENTO_DOMAIN`` will be used if the ``domain``, ``username`` or ``password`` kwargs are missing


.. code-block:: python

    import magento

    >>> magento.get_api()

    2023-02-08 03:34:20 INFO   |[ MyMagento | 127_user ]|:  Authenticating user on 127.0.0.1/path/to/magento
    2023-02-08 03:34:23 INFO   |[ MyMagento | 127_user ]|:  Logged in to user
    <magento.clients.Client object at 0x000001CA83E1A200>


...

* Added ``local`` kwarg to ``Client`` to support locally hosted Magento stores and test environments

  - By default, ``local=False``

.. code-block:: python

    from magento import Client

    >>> api = Client("127.0.0.1/path/to/magento", "username", "password", local=True)



...

* Add `since() <https://github.com/tdkorn/my-magento/blob/10aa209cdbd54b9cb6631599a2e9c7cd6475e900/magento/search.py#L190-L214>`_ and `until() <https://github.com/tdkorn/my-magento/blob/10aa209cdbd54b9cb6631599a2e9c7cd6475e900/magento/search.py#L216-L227>`_ method to `SearchQuery <https://github.com/tdkorn/my-magento/blob/10aa209cdbd54b9cb6631599a2e9c7cd6475e900/magento/search.py#L14-L313>`_ classes, which search the ``created_at`` field

  - They can be chained together and also with `add_criteria() <https://github.com/tdkorn/my-magento/blob/10aa209cdbd54b9cb6631599a2e9c7cd6475e900/magento/search.py#L44-L111>`_

.. admonition:: Example
   :class: example

   .. code-block:: python

       # Retrieve orders from the first 7 days of 2023
       >>> api.orders.since("2023-01-01").until("2023-01-07").execute()

       [<Magento Order: #000000012 placed on 2023-01-02 05:19:55>, ]


.. admonition:: Example
   :class: example

   .. code-block:: python

       # Retrieve orders over $50 placed since 2022
       >>> api.orders.add_criteria(
       ...     field="grand_total",
       ...     value="50",
       ...     condition="gteq"
       ... ).since("2022-01-01").execute()

       [<Magento Order: #000000003 placed on 2022-12-21 08:09:33>, ...]


...

* Changed `add_criteria() <https://github.com/tdkorn/my-magento/blob/10aa209cdbd54b9cb6631599a2e9c7cd6475e900/magento/search.py#L44-L111>`_ to auto-increment the filter group by default if no group is specified (ie. ``AND`` condition)

.. code-block:: python

   # Retrieving products that are over $10 AND in the category with id 15
   #
   # Before v2.1.0
   >>> api.products.add_criteria('category_id','15').add_criteria('price','10','gteq', group=1)

   # v2.1.0+
   >>> api.products.add_criteria('category_id','15').add_criteria('price','10','gteq')


...

* Changed the :attr:`.Client.BASE_URL` to not include ``"www."`` at the start (see `#8 <https://github.com/tdkorn/my-magento/issues/8>`_)
* Added unit tests for `url_for() <https://github.com/tdkorn/my-magento/blob/10aa209cdbd54b9cb6631599a2e9c7cd6475e900/magento/clients.py#L115-L140>`_
* Added Jupyter notebook examples
