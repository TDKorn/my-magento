from __future__ import annotations
import copy
from . import Model
from typing import TYPE_CHECKING, List, Optional, Set, Dict
from functools import cached_property

if TYPE_CHECKING:
    from magento import Client
    from . import Product


class Category(Model):

    """Wrapper for the ``categories`` endpoint"""

    DOCUMENTATION = 'https://adobe-commerce.redoc.ly/2.3.7-admin/tag/categories'

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
    def products(self) -> List[Product]:
        """The :class:`~.Product` s in the category"""
        return self.client.products.by_category(self) or []

    @cached_property
    def product_ids(self) -> List[int]:
        """The ``product_ids`` of the category's :attr:`~.products`"""
        return [product.id for product in self.products]

    @cached_property
    def skus(self) -> List[str]:
        """The skus of the category's :attr:`~.products`"""
        return [product.sku for product in self.products]

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
    def all_products(self) -> List[Product]:
        """"The :class:`~.Product` s in the category and in :attr:`~.all_subcategories`"""
        return self.client.products.by_category(self, search_subcategories=True) or []

    @cached_property
    def all_product_ids(self) -> Set[int]:
        """The ``product_ids`` of the products in the category and in :attr:`~.all_subcategories`"""
        return set(product.id for product in self.all_products)

    @cached_property
    def all_skus(self) -> Set[str]:
        """The skus of the products in the category and in :attr:`~.all_subcategories`"""
        return set(product.sku for product in self.all_products)
