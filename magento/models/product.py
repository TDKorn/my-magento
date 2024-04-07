from __future__ import annotations
import requests
from . import Model
from pathlib import Path
from functools import cached_property
from magento.exceptions import MagentoError
from typing import Union, TYPE_CHECKING, Optional, List, Dict

if TYPE_CHECKING:
    from magento import Client
    from . import Category, Order, OrderItem, Invoice, Customer


class Product(Model):

    """Wrapper for the ``products`` endpoint"""

    STATUS_ENABLED = 1
    STATUS_DISABLED = 2

    VISIBILITY_NOT_VISIBLE = 1
    VISIBILITY_CATALOG = 2
    VISIBILITY_SEARCH = 3
    VISIBILITY_BOTH = 4

    DOCUMENTATION = 'https://adobe-commerce.redoc.ly/2.3.7-admin/tag/products/'
    IDENTIFIER = 'sku'

    def __init__(self, data: dict, client: Client):
        """Initialize a Product object using an API response from the ``products`` endpoint

        :param data: the API response from the ``products`` endpoint
        :param client: an initialized :class:`~.Client` object
        """
        super().__init__(
            data=data,
            client=client,
            endpoint='products',
            private_keys=True
        )

    def __repr__(self):
        return f'<Magento Product: {self.sku}>'

    @property
    def excluded_keys(self):
        return ['media_gallery_entries']

    @property
    def uid(self) -> Union[str, int]:
        return self.encoded_sku

    def update_stock(self, qty: int) -> bool:
        """Updates the stock quantity

        :param qty: the new stock quantity
        """
        url = f'{self.data_endpoint()}/stockItems/{self.stock_item_id}'
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
                f'Message: {MagentoError.parse(response)}'
            )
            return False

    def update_status(self, status: int) -> bool:
        """Update the product status

        :param status: either 1 (for :attr:`~.STATUS_ENABLED`) or 2 (for :attr:`~.STATUS_DISABLED`)
        """
        if status not in [Product.STATUS_ENABLED, Product.STATUS_DISABLED]:
            raise ValueError('Invalid status provided')

        return self.update_attributes({'status': status})

    def update_price(self, price: Union[int, float]) -> bool:
        """Update the product price

        :param price: the new price
        """
        return self.update_attributes({'price': price})

    def update_special_price(self, price: Union[float, int]) -> bool:
        """Update the product special price

        :param price: the new special price
        """
        if price < self.price:
            return self.update_custom_attributes({'special_price': price})

        self.logger.error(f'Sale price for {self} must be less than current price ({self.price})')
        return False

    def update_name(self, name: str, scope: Optional[str] = None) -> bool:
        """Update the product name

        :param name: the new name to use
        :param scope: the scope to send the request on; will use the :attr:`.Client.scope` if not provided
        """
        return self.update_attributes({'name': name}, scope)

    def update_description(self, description: str, scope: Optional[str] = None) -> bool:
        """Update the product description

        :param description: the new HTML description to use
        :param scope: the scope to send the request on; will use the :attr:`.Client.scope` if not provided
        """
        return self.update_custom_attributes({'description': description}, scope)

    def update_metadata(self, metadata: dict, scope: Optional[str] = None) -> bool:
        """Update the product metadata

        :param metadata: the new ``meta_title``, ``meta_keyword`` and/or ``meta_description`` to use
        :param scope: the scope to send the request on; will use the :attr:`.Client.scope` if not provided
        """
        attributes = {k: v for k, v in metadata.items() if k in ('meta_title', 'meta_keyword', 'meta_description')}
        return self.update_custom_attributes(attributes, scope)

    def add_categories(self, category_ids: Union[int, str, List[int | str]]) -> bool:
        """Adds the product to an individual or multiple categories

        :param category_ids: an individual or list of category IDs to add the product to
        """
        if not isinstance(category_ids, list):
            if not isinstance(category_ids, (str, int)):
                raise TypeError(
                    "`category_ids` must be an individual or list of integers/strings"
                )
            category_ids = [category_ids]

        current_ids = self.custom_attributes.get('category_ids', [])
        new_ids = [id for id in map(str, category_ids) if id not in current_ids]
        return self.update_custom_attributes({"category_ids": current_ids + new_ids})

    def remove_categories(self, category_ids: Union[int, str, List[int | str]]) -> bool:
        """Removes the product from an individual or multiple categories

        :param category_ids: an individual or list of category IDs to remove the product from
        """
        if not isinstance(category_ids, list):
            if not isinstance(category_ids, (str, int)):
                raise TypeError(
                    "`category_ids` must be an individual or list of integers/strings"
                )
            category_ids = [category_ids]

        current_ids = self.custom_attributes.get('category_ids', [])
        new_ids = [id for id in current_ids if id not in map(str, category_ids)]
        return self.update_custom_attributes({'category_ids': new_ids})

    def update_attributes(self, attribute_data: dict, scope: Optional[str] = None) -> bool:
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
        * **2+ Views:** admin values are updated only for :attr:`~.website_product_attributes`

        :param attribute_data: a dictionary of product attributes to update
        :param scope: the scope to send the request on; will use the :attr:`.Client.scope` if not provided
        """
        if self.client.store.is_single_store:
            return self._update_single_store(attribute_data)

        if not self._update_attributes(attribute_data, scope):
            return False

        if website_attrs := self.client.store.filter_website_attrs(attribute_data):
            return self._update_attributes(website_attrs, scope='all')
        return True

    def update_custom_attributes(self, attribute_data: dict, scope: Optional[str] = None) -> bool:
        """Update custom attributes with scoping taken into account

        See :meth:`~update_attributes` for details

        .. admonition:: Important
           :class: important-af

           This method only supports updating **custom attributes**

        :param attribute_data: a dictionary of custom attributes to update
        :param scope: the scope to send the request on; will use the :attr:`.Client.scope` if not provided
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

        self.refresh()  # Back to default scope
        return True

    def _update_attributes(self, attribute_data: dict, scope: Optional[str] = None) -> bool:
        """Sends a PUT request to update **top-level** product attributes

        .. tip:: to update attributes or custom attributes with attribute scope taken into account,
            use :meth:`~.update_attributes` or :meth:`~.update_custom_attributes` instead

        :param attribute_data: dict containing any number of top-level attributes to update
        :param scope: the scope to send the request on; will use the :attr:`.Client.scope` if not provided
        """
        url = self.data_endpoint(scope)
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
                    f"Updated {key} for {self} to {getattr(self, key)} on scope {self.get_scope_name(scope)}")
            return True
        else:
            self.logger.error(
                f'Failed with status code {response.status_code}' + '\n' +
                f'Message: {MagentoError.parse(response)}')
            return False

    def add_product_link(self, link_type: str, linked_sku: str, position: Optional[int] = None) -> bool:
        """Adds or updates a related, up-sell, or cross-sell product link.

        .. note:: If the product link already exists for the provided SKU, this method
           will only update the link if a ``position`` is specified.

        :param link_type: the product link type; must be ``upsell``, ``related`` or ``crosssell``
        :param linked_sku: the SKU of the product to be linked
        :param position: the position of the product link; if not provided, it will be added as the last link.
        :returns: boolean indicating success of the operation.
        """
        if link_type not in ('upsell', 'crosssell', 'related'):
            raise ValueError('Invalid value for `link_type` (must be "upsell", "crosssell", or "related")')

        if not (linked_product := self.client.products.by_sku(linked_sku)):
            self.logger.error(f"Invalid SKU provided: {linked_sku}")
            return False

        current_links = self.get_product_links(link_type)
        is_already_linked = linked_product.sku in [
            link['linked_product_sku']
            for link in current_links
        ]
        if position is None:
            if is_already_linked:  # Nothing to do if it's already linked and no position is specified
                self.logger.info(f'{linked_product} is already linked to {self}')
                return True

            if current_links:  # Add it as the last linked product
                position = current_links[-1]['position'] + 1
            else:
                position = 1

        url = f'{self.data_endpoint()}/links'
        product_link = {
            'link_type': link_type,
            'linked_product_sku': linked_product.sku,
            'linked_product_type': linked_product.type_id,
            'position': position,
            'sku': self.sku,
        }
        if is_already_linked:  # Update the position
            response = self.client.put(url, payload ={
                'entity': product_link
            })
        else:  # Add a new product link
            response = self.client.post(url, payload={
                'items': [product_link]
            })
        if response.ok and response.json() is True:
            self.logger.info(
                f"{'Updated' if is_already_linked else 'Added'} {linked_product} "
                f"as a {link_type} product for {self}"
            )
            self.refresh()
            return True
        else:
            self.logger.error(
                f"Failed to {'update' if is_already_linked else 'add'} {linked_product} as a {link_type} product "
                f"for {self}.\nMessage: {MagentoError.parse(response)}"
            )
            return False
            
    def delete_product_link(self, link_type: str, linked_sku: str) -> bool:
        """Removes a related, up-sell, or cross-sell product link.

        :param link_type: the product link type; must be ``upsell``, ``related`` or ``crosssell``
        :param linked_sku: the SKU of the product link to remove
        :returns: boolean indicating success of the operation.
        """
        if link_type not in ('upsell', 'crosssell', 'related'):
            raise ValueError('Invalid value for `link_type` (must be "upsell", "crosssell", or "related")')

        url = f"{self.data_endpoint()}/links/{link_type}/{linked_sku}"
        response = self.client.delete(url)

        if response.ok and response.json() is True:
            self.logger.info(f'Deleted {linked_sku} as a {link_type} product for {self}')
            return True
        else:
            self.logger.error(
                f'Failed to delete {linked_sku} as a {link_type} product for {self}.\n'
                f'Message: {MagentoError.parse(response)}'
            )
            return False

    def get_orders(self) -> Optional[Order | List[Order]]:
        """Searches for orders that contain the product

        If the product is configurable, returns orders containing any of its child products

        :returns: orders that contain the product, as an individual or list of :class:`~.Order` objects
        """
        return self.client.orders.by_product(self)

    def get_order_items(self) -> Optional[OrderItem | List[OrderItem]]:
        """Searches for order items that contain the product

        If the product is configurable, returns order items containing any of its child products

        :returns: order items that contain the product, as an individual or list of :class:`~.OrderItem` objects
        """
        return self.client.order_items.by_product(self)

    def get_invoices(self) -> Optional[Invoice | List[Invoice]]:
        """Searches for invoices that contain the product

        If the product is configurable, returns invoices containing any of its child products

        :returns: invoices that contain the product, as an individual or list of :class:`~.Invoice` objects
        """
        return self.client.invoices.by_product(self)

    def get_customers(self) -> Optional[Customer | List[Customer]]:
        """Searches for customers that have ordered the product

        If the product is configurable, returns customers that have ordered any of its child products

        :returns: customers that have ordered the product, as an individual or list of :class:`~.Customer` objects
        """
        return self.client.customers.by_product(self)

    def delete(self) -> bool:
        """Deletes the product

        .. hint:: If you delete a product by accident, the :class:`Product` object's ``data``
         attribute will still contain the raw data, which can be used to recover it.

         Alternatively, don't delete it by accident.
        """
        url = self.data_endpoint()
        response = self.client.delete(url)

        if response.ok and response.json() is True:
            self.logger.info(f'Deleted {self}')
            return True
        else:
            self.logger.error(
                f'Failed to delete {self}. Message: {MagentoError.parse(response)}'
            )
            return False

    def get_product_links(self, link_type: str) -> List[Dict]:
        """Returns data for all product links of the specified type

        :param link_type: the product link type; must be ``upsell``, ``related`` or ``crosssell``
        """
        if link_type not in ('upsell', 'crosssell', 'related'):
            self.logger.error('Invalid link type (must be "upsell", "crosssell", or "related")')
            return []

        products = [product for product in self.product_links if product['link_type'] == link_type]
        return sorted(products, key=lambda product: product['position'])

    def get_children(self, refresh: bool = False, scope: Optional[str] = None) -> List[Product]:
        """Retrieve the child simple products of a configurable product

        :param refresh: if True, calls :meth:`~.Model.refresh` on the child products to retrieve full data
        :param scope: the scope to refresh the children on (when ``refresh=True``)
        """
        if refresh:
            for child in self.children:
                child.refresh(scope)
        return self.children

    @cached_property
    def children(self) -> List[Product]:
        """If the Product is a configurable product, returns a list of its child products"""
        if self.type_id == 'configurable':
            url = self.client.url_for(f'configurable-products/{self.encoded_sku}/children')
            if (response := self.client.get(url)).ok:
                return [self.parse(child) for child in response.json()]
            else:
                self.logger.error(f'Failed to get child products of {self}')
        else:
            self.logger.info('Only configurable products have child SKUs')
        return []

    @cached_property
    def link(self) -> str:
        """Link of the product"""
        if url_key := self.custom_attributes.get('url_key'):
            return self.client.store.active.base_url + url_key + '.html'

    @cached_property
    def categories(self) -> Optional[Category | List[Category]]:
        """Categories the product is in, returned as a list of :class:`~.Category` objects"""
        category_ids = self.custom_attributes.get('category_ids', [])
        return self.client.categories.by_list('entity_id', category_ids)

    @cached_property
    def media_gallery_entries(self) -> List[MediaEntry]:
        """The product's media gallery entries, returned as a list of :class:`MediaEntry` objects"""
        return [MediaEntry(self, entry) for entry in self.__media_gallery_entries]

    @cached_property
    def thumbnail(self) -> MediaEntry:
        """The :class:`MediaEntry` corresponding to the product's thumbnail"""
        for entry in self.media_gallery_entries:
            if entry.is_thumbnail:
                return entry

    @property
    def thumbnail_link(self) -> str:
        """Link of the product's :attr:`~.thumbnail` image"""
        if self.thumbnail:
            return self.thumbnail.link

    def get_media_by_id(self, entry_id: int) -> MediaEntry:
        """Access a :class:`MediaEntry` of the product by id

        :param entry_id: the id of the media gallery entry
        """
        for entry in self.media_gallery_entries:
            if entry.id == entry_id:
                return entry

    @property
    def encoded_sku(self) -> str:
        """URL-encoded SKU, which is used in request endpoints"""
        return self.encode(self.sku)

    @cached_property
    def option_skus(self) -> List[str]:
        """The full SKUs for the product's customizable options, if they exist

        .. hint:: When a product with customizable options is ordered, these SKUs are used by the API when
            retrieving and searching for :class:`~.Order` and :class:`~.OrderItem` data
        """
        option_skus = []
        if hasattr(self, 'options'):
            for option in self.options:
                base_sku = option['product_sku']
                for val in option['values']:
                    if val.get('sku'):
                        option_skus.append(base_sku + '-' + val['sku'])
        return option_skus

    @property
    def stock(self) -> int:
        """Current stock quantity"""
        if self.stock_item:
            return self.stock_item['qty']

    @property
    def stock_item(self) -> dict:
        """Stock data from the StockItem Interface"""
        if hasattr(self, 'extension_attributes'):  # Missing if product was retrieved by id
            if stock_data := self.extension_attributes.get('stock_item', {}):
                return stock_data
        # Use the SKU to refresh attributes with full product data
        self.refresh()
        return self.stock_item

    @property
    def stock_item_id(self) -> int:
        """Item id of the StockItem, used to :meth:`~.update_stock`"""
        if self.stock_item:
            return self.stock_item['item_id']

    @property
    def description(self) -> str:
        """Product description (as HTML)"""
        return self.custom_attributes.get('description', '')

    @property
    def special_price(self) -> float:
        """The current special (sale) price"""
        return self.custom_attributes.get('special_price')


class MediaEntry(Model):

    """Wraps a media gallery entry of a :class:`Product`"""

    MEDIA_TYPES = ['base', 'small', 'thumbnail', 'swatch']

    DOCUMENTATION = "https://adobe-commerce.redoc.ly/2.3.7-admin/tag/productsskumediaentryId"
    IDENTIFIER = "id"

    def __init__(self, product: Product, entry: dict):
        """Initialize a MediaEntry object for a :class:`Product`

        :param product: the :class:`Product` that the gallery entry is associated with
        :param entry: the json response data to use as the source data
        """
        super().__init__(
            data=entry,
            client=product.client,
            endpoint=f'products/{product.encoded_sku}/media'
        )
        self.product = product

    def __repr__(self):
        return f"<MediaEntry {self.id} for {self.product}: {self.label}>"

    def query_endpoint(self) -> None:
        """No search endpoint exists for media gallery entries"""
        return self.logger.info("There is no search interface for media gallery entries")

    @property
    def excluded_keys(self) -> List[str]:
        return []

    @property
    def is_enabled(self):
        return not self.disabled

    @property
    def is_thumbnail(self):
        return 'thumbnail' in self.types

    @cached_property
    def link(self):
        """Permalink to the image"""
        return self.client.store.active.base_media_url + 'catalog/product' + self.file

    def disable(self, scope: Optional[str] = None) -> bool:
        """Disables the MediaEntry on the given scope

        :param scope: the scope to send the request on; will use the :attr:`.Client.scope` if not provided
        """
        self.data['disabled'] = True
        return self.update(scope)

    def enable(self, scope: Optional[str] = None) -> bool:
        """Enables the MediaEntry on the given scope

        :param scope: the scope to send the request on; will use the :attr:`.Client.scope` if not provided
        """
        self.data['disabled'] = False
        return self.update(scope)

    def download(self, filename: Optional[str] = None) -> Optional[str]:
        """Downloads the MediaEntry image

        :param filename: the name of the file to save the image to; uses the filename on Magento if not provided.
        :return: the absolute path of the downloaded image file, or ``None`` if the download failed
        """
        if filename is None:
            filename = Path(self.file).name

        try:
            response = requests.get(self.link)
            response.raise_for_status()

        except requests.RequestException as e:
            self.logger.error(f"Failed to download {self}: {e}")
            return None

        fpath = Path(filename).resolve()
        with open(fpath, 'wb') as f:
            f.write(response.content)

        self.logger.info(f"Downloaded {self} to {fpath}")
        return str(fpath)

    def add_media_type(self, media_type: str, scope: Optional[str] = None) -> bool:
        """Add a media type to the MediaEntry on the given scope

        .. caution:: If the media type is already assigned to a different entry, it will be removed

        :param media_type: one of the :attr:`~.MEDIA_TYPES`
        :param scope: the scope to send the request on; will use the :attr:`.Client.scope` if not provided
        """
        if media_type in self.MEDIA_TYPES and media_type not in self.types:
            self.data['types'].append(media_type)
            return self.update(scope)

    def remove_media_type(self, media_type: str, scope: Optional[str] = None) -> bool:
        """Remove a media type from the MediaEntry on the given scope

        :param media_type: one of the :attr:`~MEDIA_TYPES`
        :param scope: the scope to send the request on; will use the :attr:`.Client.scope` if not provided
        """
        if media_type in self.types:
            self.data['types'].remove(media_type)
            return self.update(scope)

        self.logger.error(f'{media_type} is not currently assigned to {self}')
        return False

    def set_media_types(self, types: list, scope: Optional[str] = None) -> bool:
        """Set media types for the MediaEntry on the given scope

        :param types: a list containing all :attr:`~MEDIA_TYPES` to assign
        :param scope: the scope to send the request on; will use the :attr:`.Client.scope` if not provided
        """
        if not isinstance(types, list):
            raise TypeError('types must be a list')

        self.data['types'] = [t for t in types if t in self.MEDIA_TYPES]
        return self.update(scope)

    def set_position(self, position: int, scope: Optional[str] = None) -> bool:
        """Set the position of the MediaEntry on the given scope

        :param position: the position to change to
        :param scope: the scope to send the request on; will use the :attr:`.Client.scope` if not provided
        """
        if not isinstance(position, int):
            raise TypeError('position must be an int')

        self.data['position'] = position
        return self.update(scope)

    def set_alt_text(self, text: str, scope: Optional[str] = None) -> bool:
        """Set the alt text (``label``) of the MediaEntry on the given scope

        :param text: the alt text to use
        :param scope: the scope to send the request on; will use the :attr:`.Client.scope` if not provided
        """
        if not isinstance(text, str):
            raise TypeError('text must be a string')

        self.data['label'] = text
        return self.update(scope)

    def update(self, scope: Optional[str] = None) -> bool:
        """Uses the :attr:`~.data` dict to update the media entry

        .. note:: Some updates alter the data of other entries; if the update is successful, the
            associated :class:`Product` will be refreshed on the same scope to keep the data consistent

        .. tip:: If there's only 1 store view, the admin will also be updated

        :param scope: the scope to send the request on; will use the :attr:`.Client.scope` if not provided
        """
        if self.client.store.is_single_store:
            success = self._update_single_store()
        else:
            success = self._update(scope)

        self.refresh(scope)  # Get updated data if success or reset to accurate data if failed

        if success:
            self.product.refresh(scope)

        return success

    def _update_single_store(self):
        """Updates the MediaEntry data on the default store view and admin"""
        for scope in (None, 'all'):
            if not self._update(scope):
                return False  # Avoid updating admin if store update fails
        return True

    def _update(self, scope: Optional[str] = None) -> bool:
        url = self.data_endpoint(scope)
        response = self.client.put(url, payload={'entry': self.data})

        if response.ok and response.json() is True:
            self.logger.info(
                f"Updated {self} on scope {self.get_scope_name(scope)}"
            )
            return True
        else:
            self.logger.error(
                f"Failed to update {self} on scope {self.get_scope_name(scope)}"
            )
            return False


class ProductAttribute(Model):

    """Wrapper for the ``products/attributes`` endpoint"""

    DOCUMENTATION = "https://adobe-commerce.redoc.ly/2.3.7-admin/tag/productsattributes/"
    IDENTIFIER = "attribute_code"

    def __init__(self, data: dict, client: Client):
        """Initialize a ProductAttribute object using an API response from the ``products/attributes`` endpoint

        :param data: the API response from the ``products/attributes`` endpoint
        :param client: an initialized :class:`~.Client` object
        """
        super().__init__(
            data=data,
            client=client,
            endpoint='products/attributes',
            private_keys=True
        )

    def __repr__(self):
        return f"<Product Attribute: {self.attribute_code}>"

    @property
    def excluded_keys(self) -> List[str]:
        return ['options']

    @property
    def options(self):
        return self.unpack_attributes(self.__options, key='label')
