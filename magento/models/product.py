from __future__ import annotations
from magento import clients
from typing import Union
from . import Model
import requests


class Product(Model):
    STATUS_ENABLED = 1
    STATUS_DISABLED = 2

    VISIBILITY_NOT_VISIBLE = 1
    VISIBILITY_CATALOG = 2
    VISIBILITY_SEARCH = 3
    VISIBILITY_BOTH = 4

    DOCUMENTATION = 'https://magento.redoc.ly/2.3.7-admin/tag/products'

    def __init__(self, data: dict, client: clients.Client):
        """Initialize a Product object

        :param data: the API response from the ``products`` endpoint
        :param client: an initialized :class:`~.Client` object
        """
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
        """Returns the media gallery entries as a list of :class:`MediaEntry` objects"""
        if not self._media_gallery_entries:
            if entries := self.__media_gallery_entries:
                self._media_gallery_entries = [MediaEntry(self, entry) for entry in entries]
        return self._media_gallery_entries

    @property
    def thumbnail(self) -> MediaEntry:
        """Returns the :"""
        return self._get_media_entry('is_thumbnail', True)

    @property
    def thumbnail_link(self):
        if self.thumbnail:
            return self.thumbnail.link

    def get_media(self, entry_id):
        return self._get_media_entry('id', entry_id)

    def _get_media_entry(self, attribute: str, value: Union[str, int, bool], condition: str = '=='):
        """Filter media gallery entries based on attribute values.

        NOTE: by specifying params as keyword arguments, method calls can be ordered in a more natural way

        :param attribute: The media gallery attribute to filter on
        :param value: The value of the attribute to match
        :param condition: The condition used to evaluate a match on. Default is '=='
        :returns: :class:`MediaEntry` objects that match the criteria
        :rtype: MediaEntry or list[MediaEntry]

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
                    criteria = f'{value} {condition} {attr}'  # Ex. "thumbnail" in types
                else:
                    criteria = f'{attr} {condition} {value}'  # Ex. "position" < 2; "id" == 34531
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

    def get_children(self, refresh=True):
        """Retrieve the child simple products of a configurable product"""
        if self.type_id != 'configurable':  # Only configurable products have child skus
            return None

        url = self.client.url_for(f'configurable-products/{self.encoded_sku}/children')
        response = self.client.request(url)
        if response.ok:
            children = [self.parse(child) for child in response.json()]
            if refresh:
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
        else:
            print(
                f'Failed to refresh SKU {self.sku}',
                f'Error Code: {response.status_code}',
                f'Message: {response.json()["message"]}',
                sep='\n'
            )

    def update_status(self, status):
        if status not in [Product.STATUS_ENABLED, Product.STATUS_DISABLED]:
            raise ValueError('Invalid status provided')

        endpoint = f'products/{self.encoded_sku}'
        scopes = (
            self.client.url_for(endpoint),  # No scope also updates default scope
            self.client.url_for(endpoint, scope='all')  # Needed to update admin
        )
        payload = {
            "product": {
                "sku": self.sku,
                "status": status
            },
            'save_options': True
        }
        for scope in scopes:
            response = requests.put(
                url=scope,
                json=payload,
                headers=self.client.headers
            )
            if not response.ok:
                print(f'Error {response.status_code}: Failed to update product status',
                      f'Message: {response.json()}',
                      sep='\n')

        def get_status(scope_url):
            return self.client.request(scope_url).json()['status']

        self.refresh()
        success = True

        for scope in scopes:  # Verify status was updated accordingly on all scopes
            if get_status(scope) != status:
                print(f'Failed to update status on {scope}')
                success = False
        print(
            '{} Status: {}'.format(
                'Success. Updated' if success else 'Failed. Current',
                'Enabled' if self.status == Product.STATUS_ENABLED else 'Disabled')
        )

    def delete(self, scope='all'):
        url = self.client.url_for(f'products/{self.encoded_sku}', scope=scope)
        response = requests.delete(
            url=url,
            headers=self.client.headers
        )
        if response.ok:
            if response.json() is True:
                # Request product details again bc I don't trust the response :)
                if (check := self.client.request(url)).status_code == 404:
                    print(f'Deleted {self.sku}')
                    return True
                else:
                    raise RuntimeError(
                        'Product was deleted but still exists...(?)' + '\n' +
                        'Message:{}'.format(check.json())
                    )
        else:
            print(f'Failed to delete {self.sku}. Message: {response.json()["message"]}')
            return False


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

    def __init__(self, product: "Product", entry: dict):
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
