from __future__ import annotations
import copy
from . import Model, Product
from functools import cached_property
from magento.exceptions import MagentoError
from typing import TYPE_CHECKING, List, Optional, Set, Dict, Union


if TYPE_CHECKING:
    from magento import Client
    from . import Order, OrderItem, Invoice


class Category(Model):

    """Wrapper for the ``categories`` endpoint"""

    DOCUMENTATION = 'https://adobe-commerce.redoc.ly/2.3.7-admin/tag/categories'
    IDENTIFIER = 'id'

    def __init__(self, data: dict, client: Client):
        """Initialize a Category object using an API response from the ``categories`` endpoint

        :param data: raw API response
        """
        super().__init__(
            data=data,
            client=client,
            endpoint='categories'
        )

    def __repr__(self):
        return f'<Magento Category: {self.name}>'

    @property
    def excluded_keys(self):
        return ['custom_attributes']

    @cached_property
    def custom_attributes(self) -> Dict[str, str]:
        return self.unpack_attributes(self.data.get('custom_attributes'))

    @cached_property
    def subcategories(self) -> List[Category]:
        """The child categories, returned as a list of :class:`~.Category` objects

        .. note:: Only the direct child categories are returned.
           For a list of all descendants, use :attr:`~.all_subcategories`
        """
        if hasattr(self, 'children_data'):  # A list of API response dicts (when Category is from search)
            return [self.parse(child) for child in self.children_data]
        if hasattr(self, 'children') and self.children:  # String of subcategory ids (from categories/{id} endpoint)
            return self.query_endpoint().by_list('entity_id', self.children)
        else:
            return []

    @cached_property
    def subcategory_ids(self) -> List[int]:
        """The ``category_ids`` of the :attr:`~.subcategories`"""
        if hasattr(self, 'children'):
            if self.children:
                return [int(child) for child in self.children.split(',')]
            return []
        return [category.id for category in self.subcategories]

    @cached_property
    def subcategory_names(self) -> List[str]:
        """The names of the category's :attr:`~.subcategories`"""
        return [category.name for category in self.subcategories]

    @cached_property
    def all_subcategories(self) -> Optional[List[Category]]:
        """Recursively retrieves all descendants of the category"""
        if not self.subcategories:
            return []
        children = copy.deepcopy(self.subcategories)
        for child in self.subcategories:
            children.extend(child.all_subcategories)
        return children

    @cached_property
    def all_subcategory_ids(self) -> List[int]:
        """The ``category_ids`` of :attr:`~.all_subcategories`"""
        return [category.id for category in self.all_subcategories]

    @cached_property
    def products(self) -> List[Product]:
        """The :class:`~.Product` s in the category

        Alias for :meth:`get_products`
        """
        return self.get_products()

    @cached_property
    def product_ids(self) -> List[int]:
        """The ``product_ids`` of the category's :attr:`~.products`"""
        return [product.id for product in self.products]

    @cached_property
    def skus(self) -> List[str]:
        """The skus of the category's :attr:`~.products`"""
        return [product.sku for product in self.products]

    @cached_property
    def all_products(self) -> List[Product]:
        """The :class:`~.Product` s in the category and in :attr:`~.all_subcategories`

        Alias for :meth:`get_products` with ``search_subcategories=True``
        """
        return self.get_products(search_subcategories=True)

    @cached_property
    def all_product_ids(self) -> Set[int]:
        """The ``product_ids`` of the products in the category and in :attr:`~.all_subcategories`"""
        return set(product.id for product in self.all_products)

    @cached_property
    def all_skus(self) -> Set[str]:
        """The skus of the products in the category and in :attr:`~.all_subcategories`"""
        return set(product.sku for product in self.all_products)

    def get_products(self, search_subcategories: bool = False) -> Optional[Product | List[Product]]:
        """Retrieves the category's products

        :param search_subcategories: if ``True``, also retrieves products from :attr:`~.all_subcategories`
        """
        return self.client.products.by_category(self, search_subcategories) or []

    def get_orders(self, search_subcategories: bool = False) -> Optional[Order | List[Order]]:
        """Retrieve any :class:`~.Order` that contains one of the category's :attr:`~products`

        :param search_subcategories: if ``True``, also searches for orders from :attr:`~.all_subcategories`
        """
        return self.client.orders.by_category(self, search_subcategories)

    def get_order_items(self, search_subcategories: bool = False) -> Optional[OrderItem | List[OrderItem]]:
        """Retrieve any :class:`~.OrderItem` that contains one of the category's :attr:`~products`

        :param search_subcategories: if ``True``, also searches for order items from :attr:`~.all_subcategories`
        """
        return self.client.order_items.by_category(self, search_subcategories)

    def get_invoices(self, search_subcategories: bool = False) -> Optional[Invoice | List[Invoice]]:
        """Retrieve any :class:`~.Invoice` that contains one of the category's :attr:`~products`

        :param search_subcategories: if ``True``, also searches for invoices from :attr:`~.all_subcategories`
        """
        return self.client.invoices.by_category(self, search_subcategories)

    def add_product(self, product: Union[str, Product], position: Optional[int] = None) -> bool:
        """Adds a product to the category.

        .. note:: This method can also be used to update the position of a product
           that's already in the category.

        :param product: the product sku or its corresponding :class:`~.Product` object
        :param position: the product position value to use
        :return: success status
        """
        url = self.data_endpoint() + "/products"
        sku = product.encoded_sku if isinstance(product, Product) else self.encode(product)
        payload = {
            "productLink": {
                "sku": sku,
                "category_id": self.uid
            }
        }
        if isinstance(position, int):
            payload['productLink'].update({"position": position})

        response = self.client.put(url, payload)

        if response.ok and response.json() is True:
            self.logger.info(f"Added {product} to {self}")
            return True
        else:
            self.logger.error(
                f"Failed to add {product} to {self}.\nMessage: {MagentoError.parse(response)}"
            )
            return False

    def remove_product(self, product: Union[str, Product]) -> bool:
        """Removes a product from the category.

        :param product: the product sku or its corresponding :class:`~.Product` object
        :return: success status
        """
        sku = product.encoded_sku if isinstance(product, Product) else self.encode(product)
        url = f"{self.data_endpoint()}/products/{sku}"
        response = self.client.delete(url)

        if response.ok and response.json() is True:
            self.logger.info(f'Removed {product} from {self}')
            return True
        else:
            self.logger.error(
                f'Failed to remove {product} from {self}. Message: {MagentoError.parse(response)}'
            )
            return False
