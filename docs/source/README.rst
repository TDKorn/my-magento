README
=======================

**MyMagento: A Python package to help simplify interaction with the Magento 2 REST API.**


Why Use MyMagento?
********************

Once you :meth:`~.Client.authenticate` your credentials on a :class:`~.Client`,
you'll never worry about formatting a :meth:`~.Client.request` to the Magento 2 REST API again.

.. code-block:: python

    # Login using MyMagento
    from magento import Client

    api = Client('website.com','username', 'password', login=False)
    api.authenticate()

.. code-block:: shell

    2022-06-14 00:55:42 INFO   |[ MyMagento | website_username ]|:  Authenticating username on website.com...
    2022-06-14 00:55:43 INFO   |[ MyMagento | website_username ]|:  Logged in to username
