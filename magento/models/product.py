from __future__ import annotations
from magento import clients
from typing import Union, Iterable
from . import Model
import requests


class Product(Model):
    STATUS_ENABLED = 1
    STATUS_DISABLED = 2

    VISIBILITY_NOT_VISIBLE = 1
    VISIBILITY_CATALOG = 2
    VISIBILITY_SEARCH = 3
    VISIBILITY_BOTH = 4

    DOCUMENTATION = 'https://adobe-commerce.redoc.ly/2.3.7-admin/tag/products/'

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
        self._children = []

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
        """Returns the :class:`MediaEntry` corresponding to the product's thumbnail"""
        for entry in self.media_gallery_entries:
            if entry.is_thumbnail:
                return entry

    @property
    def thumbnail_link(self) -> str:
        """Returns the link to the product :attr:`~.thumbnail`"""
        if self.thumbnail:
            return self.thumbnail.link

    def get_media_by_id(self, entry_id: int) -> MediaEntry:
        """Access a :class:`MediaEntry` of the product by id"""
        for entry in self.media_gallery_entries:
            if entry.id == entry_id:
                return entry

    @property
    def encoded_sku(self) -> str:
        """URL-encoded SKU, which is required when an endpoint URL contains a SKU"""
        return self.encode(self.sku)

    @property
    def stock_item(self) -> dict:
        if hasattr(self, 'extension_attributes'):  # Missing if product was retrieved by id
            if stock_data := self.extension_attributes.get('stock_item', {}):
                return stock_data
        # Use the SKU to refresh attributes with full product data
        self.refresh()
        return self.stock_item

    @property
    def stock(self) -> int:
        if self.stock_item:
            return self.stock_item['qty']

    @property
    def stock_item_id(self) -> int:
        if self.stock_item:
            return self.stock_item['item_id']

    def get_children(self, refresh: bool = False) -> list[Product]:
        """Retrieve the child simple products of a configurable product

        :param refresh: if True, calls :meth:`~.refresh` on the child products to retrieve full data
        """
        if self.type_id != 'configurable':
            self.logger.info('Only configurable products have child SKUs')
            return []

        if not self._children:
            url = self.client.url_for(f'configurable-products/{self.encoded_sku}/children')
            response = self.client.get(url)
            if response.ok:
                self._children = [self.parse(child) for child in response.json()]
            else:
                self.logger.error(f'Failed to get child products of {self.sku}')    # Will return empty list

        if refresh:
            for child in self._children:
                child.refresh()

        return self._children

    def get_option_skus(self) -> list:
        """If there are additional options, each one has its own SKU (and API Responses use this SKU)."""
        option_skus = []
        if hasattr(self, 'options'):
            for option in self.options:
                base_sku = option['product_sku']
                for val in option['values']:
                    if val.get('sku'):
                        option_skus.append(base_sku + '-' + val['sku'])
        return option_skus

    def update_stock(self, qty: int, scope: str = ''):
        endpoint = f'products/{self.encoded_sku}/stockItems/{self.stock_item_id}'
        url = self.client.url_for(endpoint, scope)
        payload = {
            "stock_item": {
                "qty": qty,
                "is_in_stock": qty > 0
            },
            'save_options': True
        }
        response = self.client.put(url, payload)
        if response.ok:
            # Get updated product data
            self.refresh(scope)
            self.logger.info(f'Updated stock to {self.stock}')
        else:
            self.logger.error(
                f'Failed with status code {response.status_code}' + '\n' +
                f'Message: {response.json()}')

    def refresh(self, scope: str = '') -> bool:
        """Updates attributes with current product data from the API"""
        url = self.client.url_for(f'products/{self.encoded_sku}', scope)
        response = self.client.get(url)

        if response.ok:
            self.set_attrs(response.json())  # Update existing object attributes
            self.logger.info(f'Refreshed {self.sku}')
            return True

        else:
            self.logger.error(
                'Failed to refresh SKU {}\nError Code: {}\nMessage: {}'.format(
                    self.sku, response.status_code, response.json()["message"])
            )
            return False

    def update_status(self, status: int, scope: str = '') -> bool:
        """Updates the product status on the default/specified store scope (and admin)

        .. note:: The request is also sent using the ``all`` scope, since product status doesn't
           automatically update in the admin

        :param status: either 1 (for :attr:`~.STATUS_ENABLED`) or 2 (for :attr:`~.STATUS_DISABLED`)
        :param scope: the store scope to send the request to (in addition to ``all``
        """
        if status not in [Product.STATUS_ENABLED, Product.STATUS_DISABLED]:
            raise ValueError('Invalid status provided')

        endpoint = f'products/{self.encoded_sku}'
        payload = {
            "product": {
                "sku": self.sku,
                "status": status
            },
            'save_options': True
        }

        for store_code in [scope, 'all']:  # 'all' scope is needed to update admin
            url = self.client.url_for(endpoint, store_code)
            response = self.client.put(url, payload)

            if response.ok and response.json()['status'] == status:
                self.logger.info('Updated status to {} for {} on scope {}'.format(
                    "Enabled" if status == Product.STATUS_ENABLED else "Disabled", self.sku, store_code)
                )
            else:
                self.logger.error(
                    f'Error {response.status_code}: Failed to update status for {self.sku}' + '\n' +
                    f'Message: {response.json()}'
                )
                return False  # Avoid updating admin if store update fails

        self.refresh(scope)
        return self.status == status

    def delete(self, scope: str = '') -> bool:
        url = self.client.url_for(f'products/{self.encoded_sku}', scope)
        response = self.client.delete(url)

        if response.ok and response.json() is True:
            self.logger.info(f'Deleted {self.sku}')
            return True
        else:
            self.logger.error(
                f'Failed to delete {self.sku}. Message: {response.json()["message"]}'
            )
            return False


class MediaEntry(Model):

    MEDIA_TYPES = ['base', 'small', 'thumbnail', 'swatch']

    def __init__(self, product: Product, entry: dict):
        super().__init__(
            data=entry,
            client=product.client,
            endpoint=f'products/{product.encoded_sku}/media/{entry["id"]}'
        )
        self.product = product

    @property
    def excluded_keys(self):
        return []

    @property
    def is_enabled(self):
        return not self.disabled

    @property
    def is_thumbnail(self):
        return 'thumbnail' in self.types

    @property
    def link(self):
        return f'https://{self.client.domain}/media/catalog/product{self.file}'

    def disable(self) -> bool:
        self.data['disabled'] = True
        return self.update(refresh_product=False)

    def enable(self) -> bool:
        self.data['disabled'] = False
        return self.update(refresh_product=False)

    def add_media_type(self, media_type: str) -> bool:
        if media_type in self.MEDIA_TYPES and media_type not in self.types:
            self.data['types'].append(media_type)
            return self.update()

    def remove_media_type(self, media_type: str) -> bool:
        if media_type in self.types:
            self.data['types'].remove(media_type)
            return self.update()

    def set_media_types(self, types: list) -> bool:
        if not isinstance(types, list):
            raise TypeError('types must be a list')

        types = [t for t in types if t in self.MEDIA_TYPES]
        self.data['types'] = types
        return self.update()

    def set_position(self, position: int):
        if not isinstance(position, int):
            raise TypeError('position must be an int')

        self.data['position'] = position
        return self.update()

    def set_alt_text(self, text: str) -> bool:
        if not isinstance(text, str):
            raise TypeError('text must be a string')

        self.data['label'] = text
        return self.update(refresh_product=False)

    def update(self, refresh_product: bool = True) -> bool:
        """Uses the :attr:`~.data` dict to update the media entry

        .. note:: Some updates (ex. changing the position or the type) can alter the data of other media gallery
            entries,; setting ``refresh_product=True`` ensures the :class:`Product` always has accurate data

        :param refresh_product: if True, will also refresh the product after updating
        """
        url = self.client.url_for(self.endpoint)
        success = True

        response = self.client.put(url, payload={'entry': self.data})
        if response.ok and response.json() is True:
            self.logger.info(
                f'Updated media entry {self.id} for {self.product}'
            )
        else:
            success = False
            self.logger.error(
                f'Failed to update media entry {self.id} for {self.product}'
            )
        self.refresh()

        if refresh_product:
            self.product._media_gallery_entries.clear()
            self.product.refresh()

        return success

    def refresh(self) -> bool:
        url = self.client.url_for(self.endpoint)
        response = self.client.get(url)

        if response.ok:
            self.set_attrs(response.json())
            self.logger.info(f'Refreshed media entry {self.id} for {self.product}')
            return True
        else:
            self.logger.error(
                'Failed to refresh media entry {}\nError Code: {}\nMessage: {}'.format(
                    self.id, response.status_code, response.json()["message"])
            )
            return False
