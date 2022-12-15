from __future__ import annotations
from functools import cached_property
from magento import clients
from typing import Union
from . import Model, category


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
        self._categories = []
        self._children = []

    def __repr__(self):
        return f'<Magento Product: {self.sku}>'

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

    @property
    def description(self) -> str:
        return self.custom_attributes.get('description', '')

    @property
    def special_price(self) -> float:
        return self.custom_attributes.get('special_price')

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

    def get_categories(self) -> list[category.Category]:
        if not self._categories:
            for category_id in self.custom_attributes.get('category_ids', []):
                self._categories.append(self.client.categories.by_id(category_id))
        return self._categories

    def update_stock(self, qty: int) -> bool:
        """Updates the stock quantity

        :param qty: the new stock quantity
        """
        endpoint = f'products/{self.encoded_sku}/stockItems/{self.stock_item_id}'
        url = self.client.url_for(endpoint)
        payload = {
            "stock_item": {
                "qty": qty,
                "is_in_stock": qty > 0
            },
            'save_options': True
        }
        response = self.client.put(url, payload)
        if response.ok:
            self.refresh()
            self.logger.info(f'Updated stock to {self.stock} for {self}')
            return True

        else:
            self.logger.error(
                f'Failed to update stock for {self} with status code {response.status_code}' + '\n' +
                f'Message: {response.json()}'
            )
            return False

    def refresh(self, scope: str = None) -> bool:
        """Updates attributes with current product data from the API"""
        url = self.client.url_for(f'products/{self.encoded_sku}', scope)
        response = self.client.get(url)

        if response.ok:
            self.set_attrs(response.json())  # Update existing object attributes
            self.logger.info(f"Refreshed {self.sku} on scope {scope if scope else self.client.scope or 'default'}")
            return True

        else:
            self.logger.error(
                'Failed to refresh SKU {}\nError Code: {}\nMessage: {}'.format(
                    self.sku, response.status_code, response.json()["message"])
            )
            return False

    def update_status(self, status: int) -> bool:
        """Updates the product status

        :param status: either 1 (for :attr:`~.STATUS_ENABLED`) or 2 (for :attr:`~.STATUS_DISABLED`)
        """
        if status not in [Product.STATUS_ENABLED, Product.STATUS_DISABLED]:
            raise ValueError('Invalid status provided')

        return self.update_attributes({'status': status})

    def delete(self, scope: str = None) -> bool:
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

    def _update_attributes(self, attribute_data: dict, scope: str = None) -> bool:
        """Sends a PUT request to update **top-level** product attributes

        .. tip:: to update attributes or custom attributes with attribute scope taken into account,
            use :meth:`~.update_attributes` or :meth:`~.update_custom_attributes` instead

        :param attribute_data: dict containing any number of top-level attributes to update
        :param scope: the scope to send the request on; will use the :attr:`~.Client.scope` if not provided
        """
        url = self.client.url_for(f'products/{self.encoded_sku}', scope)
        payload = {
            "product": {
                "sku": self.sku
            },
            'save_options': True
        }
        payload['product'].update(attribute_data)

        response = self.client.put(url, payload)
        if response.ok:
            self.refresh(scope)
            for key in attribute_data:
                self.logger.info(
                    f"Updated {key} for {self.sku} to {getattr(self, key)} " +
                    f"on scope {scope if scope else self.client.scope or 'default'}")
            return True
        else:
            self.logger.error(
                f'Failed with status code {response.status_code}' + '\n' +
                f'Message: {response.json()}')
            return False

    def update_name(self, name: str, scope: str = None) -> bool:
        return self.update_attributes({'name': name}, scope)

    def update_description(self, description: str, scope: str = None) -> bool:
        return self.update_custom_attributes({'description': description}, scope)

    def update_metadata(self, metadata: dict, scope: str = None) -> bool:
        """Updates product metadata

        :param metadata: the new ``meta_title``, ``meta_keyword`` and/or ``meta_description`` to use
        :param scope: the store scope to update
        """
        attributes = {k: v for k, v in metadata.items() if k in ('meta_title', 'meta_keyword', 'meta_description')}
        return self.update_custom_attributes(attributes, scope)

    def update_price(self, price: Union[int, float]) -> bool:
        return self.update_attributes({'price': price})

    def update_special_price(self, price: Union[float, int]) -> bool:
        if price < self.price:
            return self.update_custom_attributes({'special_price': price})

        self.logger.error(f'Sale price for {self} must be less than current price ({self.price})')
        return False

    def update_attributes(self, attribute_data: dict, scope: str = None) -> bool:
        """Update top level product attributes with scoping taken into account

        .. note:: Product attributes can have a ``Global``, ``Store View`` or ``Website`` scope

            :Global Attributes:
                Values are updated on all store views and the admin
            :Website Attributes:
                Values are updated on all store views
            :Store View Attributes:
                Values are updated on the store view specified in the request ``scope``

        A second request will be made to update ``Store View`` and ``Website`` attributes on the admin,
        depending on how many :class:`~.Store` :attr:`~.views` you have:

        * **1 View:** admin values are updated for all attributes, regardless of scope
        * **2+ Views:** admin values are updated only for ``Website`` attributes

        :param attribute_data: a dictionary of product attributes to update
        :param scope: the scope to send the request on; will use the :attr:`~.Client.scope` if not provided
        """
        if self.client.store.is_single_store:
            return self._update_single_store(attribute_data)

        if not self._update_attributes(attribute_data, scope):
            return False

        if website_attrs := self.client.store.filter_website_attrs(attribute_data):
            return self._update_attributes(website_attrs, scope='all')
        return True

    def update_custom_attributes(self, attribute_data: dict, scope: str = None) -> bool:
        """Update custom attributes with scoping taken into account

        See :meth:`~update_attributes` for details

        .. important:: This method only supports **custom attributes**

        :param attribute_data: a dictionary of custom attributes to update
        :param scope: the scope to send the request on; will use the :attr:`~.Client.scope` if not provided
        """
        attributes = {'custom_attributes': self.pack_attributes(attribute_data)}

        if self.client.store.is_single_store:
            return self._update_single_store(attributes)

        if not self._update_attributes(attributes, scope):
            return False

        if website_attributes := self.client.store.filter_website_attrs(attribute_data):
            return self._update_attributes({'custom_attributes': self.pack_attributes(website_attributes)}, scope='all')
        return True

    def _update_single_store(self, attribute_data: dict) -> bool:
        """Internal function for updating a store with a single store view

        All attributes will be updated on the ``default`` and ``all`` scope,
        ensuring that the frontend and admin always have the same product data

        :param attribute_data: a dictionary of custom product attributes to update
        """
        for store_code in (None, 'all'):
            if not self._update_attributes(attribute_data, store_code):
                return False  # Avoid updating admin if store update fails

        self.refresh()  # Back to original scope
        return True


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

    @cached_property
    def link(self):
        return self.client.store.active.base_media_url + 'catalog/product' + self.file

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


class ProductAttribute(Model):

    def __init__(self, data: dict, client: clients.Client):
        """Initialize a ProductAttribute object

        :param data: the API response from the ``products/attributes`` endpoint
        :param client: an initialized :class:`~.Client` object
        """
        super().__init__(
            data=data,
            client=client,
            endpoint='products/attributes',
            private_keys=True
        )

    @property
    def excluded_keys(self) -> list[str]:
        return ['options']

    @property
    def options(self):
        return self.unpack_attributes(self.__options, key='label')
