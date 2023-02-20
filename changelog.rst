Changelog
----------
v2.1.1
~~~~~~~~~

* Redid the ``README.rst`` and made it slay on both GitHub and PyPi

PyPi
==========
.. image:: https://user-images.githubusercontent.com/96394652/220112582-19dfb85f-a91a-4010-90fa-68844a2c48e8.png


GitHub
===========
.. image:: https://user-images.githubusercontent.com/96394652/220112040-6101d40c-1fe6-4537-80da-d559896ae42c.png



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

* Add :meth:`~.since` and :meth:`~.until` method to .. _.SearchQuery: https://my-magento.readthedocs.io/en/v2.1.1/search.html#magento.search.SearchQuery classes, which search the ``created_at`` field

  - They can be chained together and also with :meth:`~.add_criteria`

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

* Changed :meth:`~.add_criteria` to auto-increment the filter group by default if no group is specified (ie. ``AND`` condition)

.. code-block:: python

   # Retrieving products that are over $10 AND in the category with id 15
   #
   # Before v2.1.0
   >>> api.products.add_criteria('category_id','15').add_criteria('price','10','gteq', group=1)

   # v2.1.0+
   >>> api.products.add_criteria('category_id','15').add_criteria('price','10','gteq')


...

* Changed the :attr:`.Client.BASE_URL` to not include ``"www."`` at the start (see `#8 <https://github.com/tdkorn/my-magento/issues/8>`_)
* Added unit tests for :meth:`~.url_for`
* Added Jupyter notebook examples
