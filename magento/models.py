# Everything without entity_id
from __future__ import annotations
import requests
from . import clients


class Product:
    STATUS_ENABLED = 1
    STATUS_DISABLED = 2

    VISIBILITY_NOT_VISIBLE = 1
    VISIBILITY_CATALOG = 2
    VISIBILITY_SEARCH = 3
    VISIBILITY_BOTH = 4

    DOCUMENTATION = 'https://magento.redoc.ly/2.3.7-admin/tag/products'

    def __init__(self, data: {}, client: clients.Client):
        if not isinstance(data, dict) or not isinstance(client, clients.Client):
            raise ValueError
        self.sku = None  # The only required API response field
        self.client = client
        self.set_attrs(data)

    def __str__(self):
        return f'Magento Product: {self.sku}'

    def set_attrs(self, data):
        for attr in data:
            if attr == 'custom_attributes':
                # Unpack list of custom attribute dicts into a single dict
                custom_attrs = {
                    attr['attribute_code']: attr['value']
                    for attr in data[attr]
                }
                setattr(self, attr, custom_attrs)
            else:
                # Set attribute as is for all other API response fields
                setattr(self, attr, data[attr])

    @property
    def encoded_sku(self):
        # Must URL encode forward slashes when making API requests
        return self.sku.replace('/', '%2F')

    @property
    def stock_item(self):
        if hasattr(self, 'extension_attributes'):  # May be excluded depending on request endpoint
            return self.extension_attributes.get('stock_item', {})

    @property
    def stock(self):
        if self.stock_item:
            return self.stock_item['qty']

    @property
    def stock_item_id(self):
        if self.stock_item:
            return self.stock_item['item_id']

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
            # Update existing object attributes
            self.set_attrs(response.json())
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


class Category:

    def __init__(self, json, client):
        self.json = json
        self.client = client

        self.id = json['id']
        self.parent_id = json['parent_id']
        self.name = json['name']
        self.is_active = json['is_active']
        self.position = json['position']
        self.level = json['level']
        # Only available from CategorySearch().add_criteria().execute()
        self.product_count = json.get('product_count')
        # Only available from CategorySearch().by_id()
        self.created_at = json.get('created_at')
        self.updated_at = json.get('updated_at')
        self.custom_attributes = json.get('custom_attributes', {})
        # Attributes that require API interaction (and are therefore stored)
        self._products = None
        self._subcategories = None

    @property
    def subcategories(self):
        if self._subcategories is None:  # Hasn't been checked before
            if not self.json.get('children_data'):
                if not self.json.get('children'):
                    # Data comes from those two fields; must not have subcategories
                    self._subcategories = []
                else:
                    # 'children' field is a comma separated string of child category ids
                    child_ids = self.json['children'].split(',')
                    self._subcategories = [self.client.categories.by_id(child_id) for child_id in child_ids]
            else:
                # 'children_data' is a list of child categories as (mostly) full json responses
                self._subcategories = [Category(child, self.client) for child in self.json['children_data']]

        return self._subcategories

    @property
    def subcategory_ids(self):
        if self.json.get('children'):
            return self.json['children'].split(',')
        else:
            return [category.id for category in self.subcategories]

    @property
    def subcategory_names(self):
        return [category.name for category in self.subcategories]

    @property
    def products(self):
        if self._products is None:
            products = self.client.request(self.client.url_for(f'categories/{self.id}/products'))
            self._products = [product['sku'] for product in products.json()]
        return self._products

    @property
    def all_products(self):
        """Products of the category AND its subcategories"""
        products = self.products.copy()
        for child in self.subcategories:
            products.extend(child.products)
        # In case there are products in more than one subcategory
        return set(products)

    @property
    def attributes(self):
        return {attr['attribute_code']: attr['value'] for attr in self.custom_attributes}
