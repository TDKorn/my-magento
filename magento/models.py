# Everything without entity_id
from __future__ import annotations
import requests

from abc import ABC, abstractmethod
from typing import Union
from . import clients


class Model(ABC):
    """The base class for all API response wrapper classes

    **Overview**

    * A :class:`Model` is the object representation of any Magento API response
    * Initialized using the JSON response ``data`` from any API ``endpoint``
    * Most predefined subclasses use an ``endpoint`` that can be searched with criteria
    * Access the corresponding :class:`~magento.search.SearchQuery` object via :meth:`~.query_endpoint`
    """

    def __init__(self, data: dict, client: clients.Client, endpoint: str, private_keys: bool = True):
        """Initialize a :class:`Model` object from an API response and the ``endpoint`` that it came from

        ...

        **NOTE** that the ``endpoint`` is used to:

        * Generate the :meth:`~.url_for` any requests made by subclass-specific methods
        * Match the :class:`Model` to its corresponding :class:`~magento.search.SearchQuery` object,
          which is returned by :meth:`~.query_endpoint`
        * Determine how to :meth:`~Model.parse` new :class:`Model` objects from API responses

        ...

        :param data: the JSON from an API response to use as source data
        :param client: an initialized :class:`~.Client`
        :param endpoint: the base API endpoint that the :class:`Model` represents
        :param private_keys: if set to True, will set the keys in the :attr:`~.excluded_keys` as private attributes
            (prefixed with ``__``) instead of fully excluding them

        """
        if not isinstance(data, dict):
            raise TypeError(f'Parameter "data" must be of type {dict}')
        if not isinstance(endpoint, str):
            raise TypeError(f'Parameter "endpoint" must be of type {str}')
        if not isinstance(client, clients.Client):
            raise TypeError(f'Parameter "client" must be of type {clients.Client}')

        self.data = data
        self.client = client
        self.endpoint = endpoint
        self.set_attrs(data, private_keys=private_keys)

    def set_attrs(self, data: dict, private_keys: bool = True) -> None:
        """Initializes object attributes using the JSON from an API response as the data source

        Called at the time of object initialization, but can also be used to update the source data and
        reinitialize the attributes without creating a new object

        :param data: the API response JSON to use as the object source data
        :param private_keys: if set to True, will set the :attr:`~.excluded_keys` as private attributes
            (prefixed with ``__``) instead of fully excluding them

        **Private Keys Clarification**

        Let's say that ``"status"`` is in the :attr:`~.excluded_keys`

        * No matter what, the :class:`Model` object will not have a ``status`` attribute set
        * If ``private_keys=True``, it **will** have a ``__status`` attribute set though
        * If ``private_keys=False``, then the attribute/key is completely excluded

        """
        keys = set(data) - set(self.excluded_keys)
        for key in keys:
            if key == 'custom_attributes':
                if attrs := data[key]:
                    setattr(self, key, self.unpack_attributes(attrs))
            else:
                setattr(self, key, data[key])

        if private_keys:
            private = '_' + self.__class__.__name__ + '__'
            for key in self.excluded_keys:
                setattr(self, private + key, data.get(key))

        self.data = data

    @property
    @abstractmethod
    def excluded_keys(self) -> list[str]:
        """Keys that should not be set by set_attrs() method

        :returns: list of API response keys that should not be set as attributes
        :rtype: list[str]
        """
        pass

    def query_endpoint(self):
        """Initializes and returns the :class:`~.SearchQuery` object corresponding to the Model's ``endpoint``

        :returns: a :class:`~.SearchQuery` or subclass, depending on the ``endpoint``
        :rtype: :class:`~.SearchQuery`
        """
        return self.client.search(self.endpoint)

    def parse(self, response: dict) -> Model:
        """Initializes and returns a new :class:`~.Model` object from an API response

        :param response: JSON dictionary from the API to use as source data
        :return: a :class:`~.Model` initialized from the provided ``response``; uses ``endpoint`` of calling instance
        :rtype: :class:`~.Model`
        """
        return self.query_endpoint().parse(response)

    @staticmethod
    def unpack_attributes(attributes: list[dict]) -> dict:
        """Unpacks a list of custom attribute dictionaries into a single dictionary

        **Example**

        >>> custom_attrs = [{'attribute_code': 'attr', 'value': 'val'},{'attribute_code': 'will_to_live', 'value': '0'}]
        >>> print(Model.unpack_attributes(custom_attrs))
        {'attr': 'val', 'will_to_live': '0'}

        :param attributes: a list of custom attribute dictionaries
        :returns: a single dictionary of all custom attributes formatted as ``{"attr": "val"}``

        """
        return {attr['attribute_code']: attr['value'] for attr in attributes}

    @staticmethod
    def encode(string: str) -> str:
        """URL-encode with :mod:`urllib`; used for requests that could contain special characters

        |  **Example:** requests to the ``products`` endpoint contain a ``sku`` path parameter
        |      **‣** Since a ``sku`` can contain characters like ``/`` and ``*``, it will always be encoded first
        |      **‣** See :meth:`~.by_sku` or :attr:`~.encoded_sku`

        :param string: the string to URL-encode
        """
        import urllib.parse
        return urllib.parse.quote_plus(string)


class Product(Model):
    STATUS_ENABLED = 1
    STATUS_DISABLED = 2

    VISIBILITY_NOT_VISIBLE = 1
    VISIBILITY_CATALOG = 2
    VISIBILITY_SEARCH = 3
    VISIBILITY_BOTH = 4

    DOCUMENTATION = 'https://magento.redoc.ly/2.3.7-admin/tag/products'

    def __init__(self, data: dict, client: clients.Client):
        super().__init__(
            data=data,
            client=client,
            endpoint='products',
            private_keys=True
        )
        self._media_gallery_entries = []

    def __str__(self):
        return f'Magento Product: {self.sku}'

    @property
    def excluded_keys(self):
        return ['media_gallery_entries']

    @property
    def media_gallery_entries(self) -> list[MediaEntry]:
        """Returns the media gallery entries as a list of MediaEntry objects"""
        if not self._media_gallery_entries:
            if entries := self.__media_gallery_entries:
                self._media_gallery_entries = [MediaEntry(self, entry) for entry in entries]
        return self._media_gallery_entries

    @property
    def thumbnail(self):
        return self._get_media_entry('is_thumbnail', True)

    @property
    def thumbnail_link(self):
        if self.thumbnail:
            return self.thumbnail.link

    def get_media(self, entry_id):
        return self._get_media_entry('id', entry_id)

    def _get_media_entry(self, attribute: str, value: Union[str, int, bool], condition: str = '=='):
        """Filter media gallery entries based on attribute values. Specifying params as keyword arguments allows for
        method calls to be ordered in a more natural way

        :param attribute: The media gallery attribute to filter on
        :param value: The value of the attribute to match
        :param condition: The condition used to evaluate a match on. Default is '=='

        Sample Usage:
            Get Thumbnail Image:
                product._get_media_entry(value='thumbnail', condition='in', attribute='types')
                    - Matches the media entry containing the string "thumbnail" within its "types" list
                product._get_media_entry('is_thumbnail', True)
                    - Simpler way; Matches the 'is_thumbnail' property of MediaEntry class

            Get Entries in Position 0 or 1:
                product.__get_media_entry(attribute='position', condition = '<', value=2)
                    - Matches media entries with position < 2
        """
        result = []

        if not isinstance(value, int):
            value = f'\"{value}\"'

        for entry in self.media_gallery_entries:
            if hasattr(entry, attribute):
                attr = getattr(entry, attribute)
                if condition == 'in':
                    criteria = f'{value} {condition} {attr}'    # Ex. "thumbnail" in types
                else:
                    criteria = f'{attr} {condition} {value}'    # Ex. "position" < 2; "id" == 34531
                try:
                    if eval(criteria):
                        result.append(entry)
                except Exception as e:  # All criteria within package will work. This is for anyone else (:
                    raise RuntimeError(f'Invalid Criteria: {criteria}') from e

        if len(result) == 1:
            return result[0]
        return result


    @property
    def encoded_sku(self):
        """URL-encoded SKU, which is required when an endpoint URL contains a SKU"""
        return self.encode(self.sku)

    @property
    def stock_item(self):
        if hasattr(self, 'extension_attributes'):  # Missing if product was retrieved by id
            if stock_data := self.extension_attributes.get('stock_item', {}):
                return stock_data
        # Use the SKU to refresh attributes with full product data
        self.refresh()
        return self.stock_item

    @property
    def stock(self):
        if self.stock_item:
            return self.stock_item['qty']

    @property
    def stock_item_id(self):
        if self.stock_item:
            return self.stock_item['item_id']

    def get_children(self):
        """Retrieve the child simple products of a configurable product"""
        if self.type_id != 'configurable':  # Only configurable products have child skus
            return None

        url = self.client.url_for(f'configurable-products/{self.encoded_sku}/children')
        response = self.client.request(url)
        if response.ok:
            children = [self.parse(child) for child in response.json()]
            for child in children:
                child.refresh()
            return children
        else:
            print(f'Failed to get child products of {self.sku}')
            return None

    def get_option_skus(self):
        """If there are additional options, each one has its own SKU (and API Responses use this SKU)."""
        option_skus = []
        if hasattr(self, 'options'):
            for option in self.options:
                base_sku = option['product_sku']
                for val in option['values']:
                    if val.get('sku'):
                        option_skus.append(base_sku + '-' + val['sku'])
        return option_skus

    def update_stock(self, qty):
        endpoint = f'products/{self.encoded_sku}/stockItems/{self.stock_item_id}'
        url = self.client.url_for(endpoint)
        payload = {
            "stock_item": {
                "qty": qty,
                "is_in_stock": qty > 0
            },
            'save_options': True
        }
        response = requests.put(
            url=url,
            json=payload,
            headers=self.client.headers
        )
        if response.ok:
            # Get updated product data
            self.refresh()
            print(f'Updated stock to {self.stock}')

        else:
            print(
                f'Failed with status code {response.status_code}' + '\n' +
                f'Message: {response.json()}'
            )

    def refresh(self):
        """Updates attributes with current product data from the API"""
        url = self.client.url_for(f'products/{self.encoded_sku}')
        response = self.client.request(url)
        if response.ok:
            self.set_attrs(response.json())  # Update existing object attributes
            print('Refreshed ' + self.sku)

        elif response.status_code == 401:
            self.client.authenticate()
            self.refresh()

        else:
            print(
                f'Failed to refresh SKU {self.sku}',
                f'Error Code: {response.status_code}',
                f'Message: {response.json()["message"]}',
                sep='\n'
            )


class MediaEntry(Model):
    MEDIA_MAPPING = {
        'id': int,
        'media_type': str,
        'label': str,
        'position': int,
        'disabled': bool,
        'types': list,
        'file': str
    }

    def __init__(self, product: Product, entry: dict):
        super().__init__(
            data=entry,
            client=product.client,
            endpoint='products/{}/media'.format(product.encoded_sku)
        )
        self.product = product

    @property
    def excluded_keys(self):
        return []

    @property
    def is_thumbnail(self):
        return 'thumbnail' in self.types

    @property
    def link(self):
        return f'https://{self.client.domain}/media/catalog/product{self.file}'


class Category(Model):
    DOCUMENTATION = 'https://magento.redoc.ly/2.3.7-admin/tag/categories'

    def __init__(self, data, client):
        super().__init__(
            data=data,
            client=client,
            endpoint='categories'
        )
        self._products = None  # Attributes that are stored after retrieving the first time
        self._subcategories = None

    def __str__(self):
        return f'Magento Category: {self.name}'

    @property
    def excluded_keys(self):
        return []

    @property
    def subcategories(self):
        """Retrieve and temporarily store the category's child categories"""
        if self._subcategories is None:
            if hasattr(self, 'children_data'):
                # children_data: a list of mostly complete subcategory API response dicts
                self._subcategories = [self.parse(child) for child in self.children_data]
            elif hasattr(self, 'children'):
                # children: a comma separated string of subcategory ids; self.subcategory_ids returns them as list
                self._subcategories = [self.query_endpoint().by_id(child_id) for child_id in self.subcategory_ids]
            else:
                self._subcategories = []    # Data comes from those two fields... no subcategories
        return self._subcategories

    @property
    def subcategory_ids(self):
        if hasattr(self, 'children'):
            return self.children.split(',')
        else:
            return [category.id for category in self.subcategories]

    @property
    def subcategory_names(self):
        return [category.name for category in self.subcategories]

    @property
    def products(self):
        if self._products is None:
            endpoint = self.client.url_for(f'categories/{self.id}/products')
            response = self.client.request(endpoint)
            self._products = [product['sku'] for product in response.json()]
        return self._products

    @property
    def all_products(self):
        """Products of the category AND its subcategories"""
        products = self.products.copy()
        for child in self.subcategories:
            if child.name != 'Default Category':
                products.extend(child.products)
        # In case there are products in more than one subcategory
        return set(products)
