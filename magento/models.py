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
            raise TypeError

        self.sku = None  # Required API response field
        self.client = client
        self.set_attrs(data)

    def __str__(self):
        return f'Magento Product: {self.sku}'

    def set_attrs(self, data):
        for key in data:
            if key == 'custom_attributes':  # Unpack list of custom attribute dicts into a single attribute dict
                custom_attrs = {
                    attr['attribute_code']: attr['value']
                    for attr in data['custom_attributes']
                }
                setattr(self, key, custom_attrs)
            else:
                setattr(self, key, data[key])  # Set attribute as is for all other API response fields

    @property
    def encoded_sku(self):
        # Must URL encode forward slashes when making API requests
        return self.sku.replace('/', '%2F')

    @property
    def stock_item(self):
        if hasattr(self, 'extension_attributes'):
            if stock_data := self.extension_attributes.get('stock_item', {}):  # Missing if product was retrieved by id
                return stock_data
        self.refresh()          # Use the SKU to get full product data and refresh attributes
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
            children = [Product(child, self.client) for child in response.json()]
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


class Category:
    DOCUMENTATION = 'https://magento.redoc.ly/2.3.7-admin/tag/categories'

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

    def __str__(self):
        return f'Magento Category: {self.name}'

    @property
    def subcategories(self):
        """Retrieve and temporarily store the category's child categories"""
        if self._subcategories is None:
            if self.json.get('children_data'):  # children_data: a list of mostly complete subcategory API response dicts
                self._subcategories = [Category(child, self.client) for child in self.json['children_data']]

            elif self.json.get('children'):     # children: comma separated string of subcategory ids
                self._subcategories = [self.client.categories.by_id(child_id) for child_id in self.subcategory_ids]
            else:
                self._subcategories = []        # Data comes from those two fields... no subcategories
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

    @property
    def attributes(self):
        return {attr['attribute_code']: attr['value'] for attr in self.custom_attributes}
