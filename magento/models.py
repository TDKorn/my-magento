# Everything without entity_id
from __future__ import annotations
import requests

from abc import ABC, abstractmethod
from typing import Union
from . import clients


class Model(ABC):
    """The base class for all API response wrapper classes

    Each Model subclass is a representation of an API response, typically from an endpoint that can
    be searched/filtered using search criteria. Thus, most Models also have a corresponding SearchQuery subclass,
    accessible through its query_endpoint() method
    """

    def __init__(self, data: dict, client: clients.Client, endpoint: str, private_keys: bool = True):
        """Initialize a Model object using the json dict from an API response

        :param data: The API response to use as the source data for the object

        :param client: An initialized Client object. Note that the Client does not need to be logged in, or have a
            valid access token; the credentials will be authenticated as needed

        :param endpoint: The base endpoint that will be used for any API requests; used to match the object with its
            corresponding SearchQuery object, if it exists

        :param private_keys: If set to True, the keys denoted in the excluded_keys property will be set as attributes
            prefixed with "_". For example, if "status" is an excluded key,  and private_keys=True, the object
            will be initialized with an "_status" attribute instead of completely excluding it.
        """

        if not isinstance(data, dict):
            raise TypeError(f'Parameter "data" must be of type {dict}')
        if not isinstance(endpoint, str):
            raise TypeError(f'Parameter "endpoint" must be of type {str}')
        if not isinstance(client, clients.Client):
            raise TypeError(f'Parameter "client" must be of type {clients.Client}')

        self.client = client
        self.endpoint = endpoint
        self.set_attrs(data, private_keys=private_keys)

    def set_attrs(self, data: dict, private_keys: bool = True) -> None:
        """Sets object attributes, using an API response dict as the data source

        :param data: The API response to use as the object source data
        :param private_keys: If set to True, will set the keys in the "excluded_keys" property as attributes
                                prefixed with an "_", instead of fully excluding them
        """
        keys = set(data) - set(self.excluded_keys)
        for key in keys:
            if key == 'custom_attributes':
                if attrs := data[key]:
                    setattr(self, key, self.unpack_attributes(attrs))
            else:
                setattr(self, key, data[key])

        if private_keys:
            for key in self.excluded_keys:
                setattr(self, "_" + key, data.get(key))

    @property
    @abstractmethod
    def excluded_keys(self) -> list[str]:
        """Keys that should not be set by set_attrs() method

        :returns the list of API response keys that should not be set as attributes
        """
        pass

    @staticmethod
    def unpack_attributes(attributes: list):
        """Unpacks a list of custom attribute dictionaries into a single dictionary

        :param attributes: A list of custom attribute dictionaries of the form
                            [{'attribute_code': 'attr', 'value': 'val'},]
        """
        return {attr['attribute_code']: attr['value'] for attr in attributes}

    def query_endpoint(self):
        """Depending on the endpoint, will return either a SearchQuery or a SearchQuery subclass"""
        return self.client.search(self.endpoint)

    def parse(self, response: dict):
        """If a SearchQuery subclass exists, initializes a Model of the same type from an API response

        :param response: The API response dict to generate the object from
        """
        return self.query_endpoint().parse(response)


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

    def __str__(self):
        return f'Magento Product: {self.sku}'

    @property
    def excluded_keys(self):
        return ['media_gallery_entries']

    @property
    def media_gallery_entries(self):
        return [MediaEntry(self, entry) for entry in self._media_gallery_entries]

    @property
    def thumbnail(self):
        return self._get_media_entry('thumbail', 'in', 'types')

    def get_media(self, entry_id):
        return self._get_media_entry('id', '==', entry_id)

    def _get_media_entry(self, val: Union[str, int], condition: str, attribute: str):
        if not isinstance(val, int):
            val = f'\"{val}\"'

        for entry in self.media_gallery_entries:
            if hasattr(entry, attribute):
                attr = getattr(entry, attribute)
                criteria = f'{val} {condition} {attr}'

                try:
                    if eval(criteria):
                        return entry

                except Exception as e:
                    raise RuntimeError(f'Invalid Criteria: {criteria}') from e

    @property
    def thumbnail_link(self):
        return self.thumbnail.link

    @property
    def encoded_sku(self):
        # Must URL encode forward slashes when making API requests
        return self.sku.replace('/', '%2F')

    @property
    def stock_item(self):
        if hasattr(self, 'extension_attributes'):
            if stock_data := self.extension_attributes.get('stock_item', {}):  # Missing if product was retrieved by id
                return stock_data
        self.refresh()  # Use the SKU to refresh attributes with full product data
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
        if self.type_id != 'configurable':
            return None  # Only configurable products have child skus

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
        # self.id = None  # Attributes that are referenced within class methods (and are required response fields)
        # self.name = None
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
