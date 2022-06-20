MyMagento: Example Usage
================================

Login to a Client
--------------------------------

Use the :class:`~.Client` to login to the API

.. code-block:: python

    # Login to Magento API using MyMagento
    from magento import Client

    >>> api = Client('website.com','username', 'password')

If ``login=False`` is specified, the :class:`~.Client` will not request an :attr:`~.ACCESS_TOKEN`
until you call :meth:`~.authenticate`

.. code-block:: python

    >>> api = Client("website.com", "username", "password", login=False)
    >>> api.authenticate()

.. code-block:: shell

    2022-06-14 00:55:42 INFO   |[ MyMagento | website_username ]|:  Authenticating username on website.com...
    2022-06-14 00:55:43 INFO   |[ MyMagento | website_username ]|:  Logged in to username
