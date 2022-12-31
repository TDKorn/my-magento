from __future__ import annotations
import copy
from . import Model
from typing import TYPE_CHECKING
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
    def custom_attributes(self):
        return self.unpack_attributes(self.__custom_attributes)

    @cached_property
    def subcategories(self) -> list[Category]:
        """Returns a list of the category's child categories"""
        if hasattr(self, 'children_data'):  # A list of API response dicts (present when Category is from search result)
            return [self.parse(child) for child in self.children_data]
        if hasattr(self, 'children'):  # String of subcategory ids (present when Category is retrieved by id)
            return [self.query_endpoint().by_id(child_id) for child_id in self.subcategory_ids]
        else:
            return []

    @cached_property
    def subcategory_ids(self) -> list[int]:
        """Returns the ids of the category's child categories"""
        if hasattr(self, 'children'):
            if self.children:
                return [int(child) for child in self.children.split(',')]
            return []
        return [category.id for category in self.subcategories]

    @cached_property
    def subcategory_names(self) -> list[str]:
        """Returns the names of the category's child categories"""
        return [category.name for category in self.subcategories]

    @cached_property
    def skus(self) -> list[str]:
        """Returns the SKUs of products in the category"""
        endpoint = self.client.url_for(f'categories/{self.id}/products')
        if (response := self.client.get(endpoint)).ok:
            return [product['sku'] for product in response.json()]

    @cached_property
    def all_skus(self) -> set[str]:
        """Returns the SKUs of products in the category and all of its :attr:`~.subcategories`"""
        skus = copy.deepcopy(self.skus)
        for child in self.subcategories:
            skus.extend(child.all_skus)
        return set(skus)

    @cached_property
    def products(self) -> list[Product]:
        """Returns the :class:`~.Product`s in the category"""
        return self.client.products.by_skulist(self.skus)

    @cached_property
    def all_products(self) -> list[Product]:
        """Returns the :class:`~.Product`s in the category and all of its :attr:`~.subcategories`"""
        return self.client.products.by_skulist(self.all_skus)
